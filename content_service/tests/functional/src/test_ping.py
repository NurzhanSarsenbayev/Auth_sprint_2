import json
import base64

import pytest
from aiohttp import ClientSession
from http import HTTPStatus
import jwt
import time
import uuid

from functional.settings import settings


# ----- helpers -----
def generate_jwt(secret: str, kid: str, payload: dict) -> str:
    """Собираем тестовый JWT с заголовком kid."""
    headers = {"kid": kid, "alg": "HS256"}
    return jwt.encode(payload, secret, algorithm="HS256", headers=headers)


@pytest.mark.asyncio
async def test_ping_guest(http_session: ClientSession):
    """Без Authorization → должен вернуться guest principal"""
    async with http_session.get(
        f"http://{settings.API_HOST}:{settings.API_PORT}/api/v1/ping"
    ) as resp:
        data = await resp.json()

    assert resp.status == HTTPStatus.OK
    assert data["principal"] == "guest"


@pytest.mark.asyncio
async def test_ping_with_valid_jwt(http_session: ClientSession, redis_client):
    """С валидным JWT → principal из токена"""
    kid = "test-key"
    secret = "test-secret"
    payload = {
        "sub": str(uuid.uuid4()),
        "email": "user@example.com",
        "iat": int(time.time()),
        "exp": int(time.time()) + 3600,
        "type": "access",
    }

    # генерируем токен через raw secret
    token = generate_jwt(secret, kid, payload)

    # JWKS в Redis (ключ должен быть base64url!)
    k = base64.urlsafe_b64encode(secret.encode()).rstrip(b"=").decode()
    jwks_key = {
        "keys": [
            {
                "kid": kid,
                "kty": "oct",
                "alg": "HS256",
                "k": k,
                "use": "sig",
            }
        ]
    }
    await redis_client.set("auth:jwks", json.dumps(jwks_key))

    # Act
    async with http_session.get(
        f"http://{settings.API_HOST}:{settings.API_PORT}/api/v1/ping",
        headers={"Authorization": f"Bearer {token}"}
    ) as resp:
        data = await resp.json()

    print("📥 VALID JWT RESPONSE:", resp.status, data)

    # Assert
    assert resp.status == HTTPStatus.OK
    assert data["principal"]["email"] == "user@example.com"


@pytest.mark.asyncio
async def test_ping_with_invalid_jwt(http_session: ClientSession):
    """С битым JWT → 401 Unauthorized"""
    bad_token = "Bearer abc.def.ghi"

    async with http_session.get(
        f"http://{settings.API_HOST}:{settings.API_PORT}/api/v1/ping",
        headers={"Authorization": bad_token}
    ) as resp:
        # важно: тут ожидаем JSON с detail
        data = await resp.json(content_type=None)

    print("📥 INVALID JWT RESPONSE:", resp.status, data)

    assert resp.status == HTTPStatus.UNAUTHORIZED
    assert "detail" in data
    assert data["detail"] == "Invalid token"


@pytest.mark.asyncio
async def test_ping_degraded_to_guest(
        http_session: ClientSession,
        redis_client):
    """Если JWKS отсутствует → сервис не падает, а даёт guest"""
    # Arrange: очищаем Redis, чтобы JWKS не было
    await redis_client.flushdb()

    # Act
    async with http_session.get(
        f"http://{settings.API_HOST}:{settings.API_PORT}/api/v1/ping"
    ) as resp:
        data = await resp.json()

    # Assert
    assert resp.status == HTTPStatus.OK
    assert data["principal"] == "guest"
