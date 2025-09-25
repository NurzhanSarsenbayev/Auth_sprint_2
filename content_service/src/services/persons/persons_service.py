from typing import List, Optional
from uuid import UUID

from elasticsearch import AsyncElasticsearch
from redis.asyncio import Redis

from src.services.base import BaseService
from models.person import Person

from services.persons.persons_fetchers import (fetch_persons_paginated,
                                               fetch_person_by_id,
                                               fetch_person_by_name)


class PersonService(BaseService):
    def __init__(self, cache, search, ttl: int = 300):
        super().__init__(cache, search, ttl)

    async def list_persons(self, size: int = 100, page: int = 1) -> List[Person]:

        cache_key = self.make_cache_key("list_persons", page=page, size=size)

        return await self.get_or_set_cache(
            cache_key,
            fetch_fn=lambda: fetch_persons_paginated(self.search, page, size),
            serializer=lambda persons: [p.dict() for p in persons],
            deserializer=lambda cached: [Person(**p) for p in cached],
        )

    async def get_person_by_id(self, person_id: UUID) -> Optional[Person]:
        cache_key = self.make_cache_key("id_persons", person_id=person_id)

        return await self.get_or_set_cache(
            cache_key,
            fetch_fn=lambda: fetch_person_by_id(self, person_id),
            serializer=lambda person: person.dict() if person else None,
            deserializer=lambda cached: Person(**cached) if cached else None,
        )

    async def search_persons(self, query_str: str) -> List[Person]:
        cache_key = self.make_cache_key("search_persons", query=query_str)

        return await self.get_or_set_cache(
            cache_key,
            fetch_fn=lambda: fetch_person_by_name(self, query_str),
            serializer=lambda persons: [p.dict() for p in persons],
            deserializer=lambda cached: [Person(**p) for p in cached],
        )
