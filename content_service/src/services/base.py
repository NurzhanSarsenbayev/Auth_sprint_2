import json
from typing import Any, Callable, Awaitable, TypeVar

from db.es_storage import ElasticsearchStorage
from db.redis_storage import RedisStorage

T = TypeVar("T")

class BaseService:
    def __init__(self, cache: RedisStorage, search: ElasticsearchStorage, ttl: int = 3):
        self.cache = cache
        self.search = search
        self.ttl = ttl

    async def get_cache(self, key: str) -> Any | None:
        cached = await self.cache.get(key)
        if cached:
            try:
                return json.loads(cached)  # словарь / список
            except Exception:
                return cached  # Pydantic raw или строка
        return None


    async def set_cache(self, key: str, value: Any) -> None:
        if hasattr(value, "json"):
            to_store = value.json()
        else:
            to_store = json.dumps(value, default=str)
        await self.cache.set(key, to_store, ex=self.ttl)

    async def get_or_set_cache(
        self,
        key: str,
        fetch_fn: Callable[[], Awaitable[T]],
        serializer: Callable[[T], Any] | None = None,
        deserializer: Callable[[Any], T] | None = None,
    ) -> T:
        cached = await self.get_cache(key)

        if cached is not None:
            if deserializer:
                return deserializer(cached)
            return cached

        data = await fetch_fn()

        to_cache = serializer(data) if serializer else data
        await self.set_cache(key, to_cache)

        return data

    async def search_index(self, index: str, body: dict) -> dict:
        return await self.search.search(index=index, body=body)

    async def get_by_id(self, index: str, doc_id: str) -> dict:
        return await self.search.get(index=index, id=doc_id)

    def make_cache_key(self, prefix: str, **kwargs) -> str:
        parts = [f"{k}={v}" for k, v in kwargs.items()]
        return f"{prefix}:" + ":".join(parts)