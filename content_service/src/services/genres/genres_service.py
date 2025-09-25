from typing import List, Optional
from uuid import UUID

from models.genre import Genre

from services.base import BaseService
from services.genres.genre_fetchers import (fetch_genres_paginated,
                                            fetch_genre_by_id,
                                            fetch_genre_by_name)

class GenreService(BaseService):
    def __init__(self, cache, search, ttl: int = 10):
        super().__init__(cache, search, ttl)

    async def list_genres(self, page: int = 1, size: int = 50) -> List[Genre]:
        cache_key = self.make_cache_key("list_genres", page=page, size=size)
        return await self.get_or_set_cache(
            cache_key,
            fetch_fn=lambda: fetch_genres_paginated(self.search, page, size),
            serializer=lambda genres: [g.dict() for g in genres],
            deserializer=lambda cached: [Genre(**g) for g in cached],
        )

    async def search_genres(self, query_str: str) -> List[Genre]:
        cache_key = self.make_cache_key("search_genres", query=query_str)

        return await self.get_or_set_cache(
            cache_key,
            fetch_fn=lambda: fetch_genre_by_name(self, query_str),
            serializer=lambda genres: [g.dict() for g in genres],
            deserializer=lambda cached: [Genre(**g) for g in cached],
        )

    async def get_genre_by_id(self, genre_id: UUID) -> Optional[Genre]:
        cache_key = self.make_cache_key("genre", genre_id=genre_id)

        return await self.get_or_set_cache(
            cache_key,
            fetch_fn=lambda: fetch_genre_by_id(self, genre_id),
            serializer=lambda g: g.dict() if g else None,
            deserializer=lambda cached: Genre(**cached) if cached else None,
        )