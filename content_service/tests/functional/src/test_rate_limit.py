import pytest
import asyncio
import jwt
import time
import uuid
import base64
import json

from http import HTTPStatus

from functional.settings import settings


def generate_jwt(secret: str, kid: str, payload: dict) -> str:
    """Собираем тестовый JWT с заголовком kid."""
    headers = {"kid": kid, "alg": "HS256"}
    return jwt.encode(payload, secret, algorithm="HS256", headers=headers)


@pytest.mark.asyncio
async def test_rate_limiting(http_session, redis_client):
    url = f"http://{settings.API_HOST}:{settings.API_PORT}/api/v1/ping"

    await redis_client.flushdb()
    ok_responses = 0
    too_many_responses = 0

    headers = {"X-Forwarded-For": "127.0.0.1"}  # ⚡ фиксируем IP

    for i in range(7):
        async with http_session.get(url, headers=headers) as resp:
            print(f"REQ {i+1}: status={resp.status}")
            if resp.status == HTTPStatus.OK:
                ok_responses += 1
            elif resp.status == HTTPStatus.TOO_MANY_REQUESTS:
                too_many_responses += 1
        await asyncio.sleep(0.05)

    assert ok_responses == 5, f"Ожидалось 5 успешных, а было {ok_responses}"
    assert too_many_responses >= 1, "Rate limiting не сработал → нет 429"


@pytest.mark.asyncio
async def test_rate_limiting_with_jwt(http_session, redis_client):
    """Rate limiting с авторизованным пользователем"""

    url = f"http://{settings.API_HOST}:{settings.API_PORT}/api/v1/ping"

    await redis_client.flushdb()

    kid = "rl-key"
    secret = "rl-secret"
    payload = {
        "sub": str(uuid.uuid4()),
        "email": "ratelimit@example.com",
        "iat": int(time.time()),
        "exp": int(time.time()) + 3600,
        "type": "access",
    }
    token = generate_jwt(secret, kid, payload)

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

    ok_responses = 0
    too_many_responses = 0

    for i in range(7):
        async with http_session.get(
            url, headers={"Authorization": f"Bearer {token}"}
        ) as resp:
            print(f"REQ {i+1} [JWT]: path=/ping, status={resp.status}")
            if resp.status == HTTPStatus.OK:
                ok_responses += 1
            elif resp.status == HTTPStatus.TOO_MANY_REQUESTS:
                too_many_responses += 1

        await asyncio.sleep(0.05)

    assert ok_responses == 5, \
        f"Ожидалось 5 успешных запросов, а было {ok_responses}"
    assert too_many_responses >= 1, \
        "Rate limiting не сработал с JWT → нет 429"
