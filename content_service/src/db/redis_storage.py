import redis.asyncio as redis
from typing import Any, Optional

from .protocols import CacheStorageProtocol


class RedisStorage(CacheStorageProtocol):
    """Реализация кэша на Redis."""

    def __init__(self, redis_url: str):
        self._redis_url = redis_url
        self._redis: Optional[redis.Redis] = None

    async def connect(self):
        """Создать подключение к Redis."""
        self._redis = await redis.from_url(
            self._redis_url,
            encoding="utf-8",
            decode_responses=True,
        )

    async def close(self):
        """Закрыть соединение."""
        if self._redis:
            await self._redis.close()

    async def get(self, key: str) -> Optional[Any]:
        if not self._redis:
            raise RuntimeError("Redis is not connected")
        return await self._redis.get(key)

    async def set(self, key: str, value: Any, expire: Optional[int] = None) -> None:
        if not self._redis:
            raise RuntimeError("Redis is not connected")
        await self._redis.set(key, value, ex=expire)