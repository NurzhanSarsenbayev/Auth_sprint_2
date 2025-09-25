from elasticsearch import AsyncElasticsearch
from typing import Optional

from .protocols import SearchStorageProtocol


class ElasticsearchStorage(SearchStorageProtocol):
    """Реализация поискового хранилища на Elasticsearch."""

    def __init__(self, hosts: list[str]):
        self._es = AsyncElasticsearch(hosts=hosts)

    async def close(self):
        """Закрыть соединение."""
        await self._es.close()

    async def get(self, index: str, id: str) -> Optional[dict]:
        try:
            doc = await self._es.get(index=index, id=id)
            return doc["_source"]
        except Exception:  # NotFoundError и прочее
            return None

    async def search(
            self,
            index: str,
            query: dict | None = None,
            body: dict | None = None,
            size: int = 10,
            from_: int = 0,
            scroll: str | None = None,
    ):
        if body is None:
            body = {"query": query}  # только если передан обычный фильтр
        resp = await self._es.search(
            index=index,
            body=body,
            size=size if body.get("size") is None else None,
            from_=from_
        )
        return resp