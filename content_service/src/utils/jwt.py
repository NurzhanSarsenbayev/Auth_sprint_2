import json
import httpx
from jose import jwt, jwk
from jose.utils import base64url_decode
from fastapi import HTTPException

from core.config import settings
from db.protocols import CacheStorageProtocol

JWKS_CACHE_KEY = "auth:jwks"

async def get_jwks(cache: CacheStorageProtocol) -> dict:
    """Получает JWKS из кэша или Auth Service"""
    cached = await cache.get(JWKS_CACHE_KEY)
    if cached:
        return json.loads(cached)

    try:
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.get(f"{settings.auth_url}/.well-known/jwks.json")
            resp.raise_for_status()
            jwks = resp.json()
    except Exception:
        raise HTTPException(status_code=503, detail="Auth service unavailable")

    # сохраняем в RedisStorage
    await cache.set(JWKS_CACHE_KEY, json.dumps(jwks), ex=600)
    return jwks


async def decode_token(token: str, cache: CacheStorageProtocol) -> dict:
    jwks = await get_jwks(cache)
    headers = jwt.get_unverified_header(token)
    kid = headers.get("kid")

    key = next((k for k in jwks["keys"] if k["kid"] == kid), None)
    if not key:
        raise HTTPException(status_code=401, detail="Unknown key id")

    try:
        payload = jwt.decode(
            token,
            key,  # 👈 передаём сам словарь из JWKS
            algorithms=["RS256"],
            options={"verify_aud": False},
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except Exception as e:
        print("❌ JWT decode error:", e)
        raise HTTPException(status_code=401, detail="Invalid token")

    if payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="Not an access token")

    return payload