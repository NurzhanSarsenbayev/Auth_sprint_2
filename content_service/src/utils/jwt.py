import json
import logging

import httpx
from core.config import settings
from db.protocols import CacheStorageProtocol
from fastapi import HTTPException, status
from jose import ExpiredSignatureError, JWTError, jwt
from jose.utils import base64url_decode

logger = logging.getLogger(__name__)
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
    try:
        jwks = await get_jwks(cache)
        headers = jwt.get_unverified_header(token)
        kid = headers.get("kid")

        key = next((k for k in jwks["keys"] if k["kid"] == kid), None)
        if not key:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unknown key id")

        if key["kty"] == "oct":
            try:
                secret = base64url_decode(key["k"].encode())
            except Exception as e:
                logger.error("Bad JWKS key encoding: %s", e)
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid secret encoding"
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Unsupported key type"
            )

        alg = key.get("alg", "HS256")

        payload = jwt.decode(
            token,
            secret,
            algorithms=[alg],
            options={"verify_aud": False},
        )

    except ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except JWTError as e:
        logger.warning("JWTError: %s", e)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except HTTPException:
        raise  # пробрасываем как есть
    except Exception as e:
        logger.exception("Unexpected error in decode_token: %s", e)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    if payload.get("type") != "access":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not an access token")

    return payload
