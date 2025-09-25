from typing import List, Optional
from uuid import UUID

from models.film import Film
from models.film_short import FilmShort

from services.base import BaseService
from services.films.film_fetchers import (fetch_films_list,
                                          fetch_film_by_id,
                                          fetch_short_film_by_name)

class FilmService(BaseService):
    def __init__(self, cache, search, ttl: int = 10):
        super().__init__(cache, search, ttl)

    async def list_films(
        self, page: int = 1, size: int = 50, sort: str = "-imdb_rating"
    ) -> List[FilmShort]:
        cache_key = self.make_cache_key("list_films", page=page, size=size, sort=sort)

        return await self.get_or_set_cache(
            cache_key,
            fetch_fn=lambda: fetch_films_list(self, page, size, sort),
            serializer=lambda films: [f.dict() for f in films],
            deserializer=lambda cached: [FilmShort(**f) for f in cached],
        )

    async def search_films(self, query_str: str, page: int = 1, size: int = 50) -> List[FilmShort]:
        cache_key = self.make_cache_key("search_films", query=query_str, page=page, size=size)

        return await self.get_or_set_cache(
            cache_key,
            fetch_fn=lambda: fetch_short_film_by_name(self, query_str, page, size),
            serializer=lambda films: [f.dict() for f in films],
            deserializer=lambda cached: [FilmShort(**f) for f in cached],
        )

    async def get_film_by_id(self, film_uuid: UUID) -> Optional[Film]:
        cache_key = self.make_cache_key("film", uuid=film_uuid)

        return await self.get_or_set_cache(
            cache_key,
            fetch_fn=lambda: fetch_film_by_id(self, film_uuid),
            serializer=lambda film: film.dict() if film else None,
            deserializer=lambda cached: Film(**cached) if cached else None,
        )