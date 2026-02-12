from uuid import UUID

from models.film import Film
from models.film_short import FilmShort
from services.films.film_parsers import parse_film, parse_film_short
from services.films.film_queries import all_films_query, search_films_query


async def fetch_films_list(service, page: int, size: int, sort: str) -> list[FilmShort]:
    resp = await service.search_index("movies", all_films_query(page, size, sort))
    return [parse_film_short(doc) for doc in resp["hits"]["hits"]]


async def fetch_film_by_id(service, film_uuid: UUID) -> Film | None:
    resp = await service.get_by_id("movies", str(film_uuid))
    return parse_film(resp)


async def fetch_short_film_by_name(service, query_str: str, page: int = 1, size: int = 10):
    resp = await service.search_index("movies", search_films_query(query_str, page, size))
    return [parse_film_short(doc) for doc in resp["hits"]["hits"]]
