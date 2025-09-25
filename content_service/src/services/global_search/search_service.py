from typing import Any, Dict
from services.base import BaseService
from services.films.films_service import FilmService
from services.persons.persons_service import PersonService
from services.genres.genres_service import GenreService
from services.global_search.search_fetchers import fetch_search_all
from models.film_short import FilmShort
from models.genre import Genre
from models.person import Person

class SearchService(BaseService):
    def __init__(self, cache, search, film_service: FilmService, person_service: PersonService, genre_service: GenreService, ttl: int = 10):
        super().__init__(cache, search, ttl)
        self.film_service = film_service
        self.person_service = person_service
        self.genre_service = genre_service

    async def search_all(self, query: str, page: int = 1, size: int = 50) -> Dict[str, Any]:
        cache_key = self.make_cache_key("search_all", query=query, page=page, size=size)

        return await self.get_or_set_cache(
            cache_key,
            fetch_fn=lambda: fetch_search_all(self, query, page, size),
            serializer=lambda data: {
                "films": [f.dict() for f in data["films"]],
                "persons": [p.dict() for p in data["persons"]],
                "genres": [g.dict() for g in data["genres"]],
            },
            deserializer=lambda cached: {
                "films": [FilmShort(**f) for f in cached["films"]],
                "persons": [Person(**p) for p in cached["persons"]],
                "genres": [Genre(**g) for g in cached["genres"]],
            },
        )