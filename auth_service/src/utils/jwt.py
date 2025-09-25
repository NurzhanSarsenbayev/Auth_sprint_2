import uuid
import jwt
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from fastapi import HTTPException, status
from redis.asyncio import Redis

from core.config import settings


# ---------- Константы ----------
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7


# ---------- Генерация ----------
def create_token(data: dict, expires_delta: timedelta, token_type: str) -> str:
    """Универсальная функция генерации токенов"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    jti = str(uuid.uuid4())  # уникальный ID токена
    to_encode.update({"exp": expire, "type": token_type, "jti": jti})

    return jwt.encode(
        to_encode,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def create_access_token(data: dict) -> str:
    return create_token(
        data, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES), "access"
    )


def create_refresh_token(data: dict) -> str:
    return create_token(
        data, timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS), "refresh"
    )


def create_token_pair(user_id: str, email: str) -> Dict[str, str]:
    """Вернуть пару access/refresh токенов"""
    payload = {"sub": user_id, "email": email}
    return {
        "access_token": create_access_token(payload),
        "refresh_token": create_refresh_token(payload),
        "token_type": "bearer",
    }


# ---------- Blacklist ----------
async def is_token_blacklisted(redis: Optional[Redis], jti: str) -> bool:
    """Проверить, есть ли токен в blacklist"""
    if not redis:
        return False
    return await redis.exists(f"blacklist:{jti}") == 1


# ---------- Декод + проверка ----------
async def decode_token(
        token: str, redis: Optional[Redis] = None) -> dict[str, Any]:
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )

    # Проверка blacklist
    jti = payload.get("jti")
    if jti and await is_token_blacklisted(redis, jti):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token revoked"
        )

    return payload


# ---------- TTL ----------
def get_token_ttl(token: str) -> int:
    """Вернуть TTL токена в секундах (для Redis)"""
    payload = jwt.decode(
        token,
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm],
        options={"verify_exp": False},
    )
    exp = payload.get("exp")
    if not exp:
        return 0
    now = datetime.now(timezone.utc).timestamp()
    return max(0, int(exp - now))
