from uuid import UUID

from services.genres.genre_queries import all_genres_query, genre_by_id_query, search_genres_query
from services.genres.genre_parsers import parse_genres_from_agg, parse_genre_from_hit, parse_genres_with_filter
from typing import List, Optional
from models.genre import Genre
from services.utils.paginator import Paginator


async def fetch_genres_list(search, size: int = 1000) -> List[Genre]:
    query = all_genres_query(size=size)
    resp = await search.search(index="movies", body=query)
    return parse_genres_from_agg(resp)

async def fetch_genres_paginated(search, page: int, size: int) -> list[Genre]:
    all_genres = await fetch_genres_list(search)
    return Paginator.paginate(all_genres, page, size, Genre)

async def fetch_genre_by_id(service, genre_uuid: UUID) -> Optional[Genre]:
    resp = await service.search_index("movies", genre_by_id_query(genre_uuid))
    return parse_genre_from_hit(resp["hits"]["hits"], genre_uuid)

async def fetch_genre_by_name(service, query_str) -> List[Genre]:
    resp = await service.search_index("movies", search_genres_query(query_str))
    return parse_genres_with_filter(resp["hits"]["hits"], query_str)