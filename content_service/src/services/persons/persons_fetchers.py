from uuid import UUID

from services.persons.person_queries import (all_persons_query,
                                             person_by_id_query,
                                             search_person_query)

from services.persons.person_parsers import (parse_persons_from_agg,
                                             parse_person_with_films,
                                             parse_persons_with_name)

from typing import List, Optional
from models.person import Person
from services.utils.paginator import Paginator

async def fetch_persons_list(search, size: int = 1000, page: int =1) -> List[Person]:
    """
    Достаёт всех персон из ES через агрегации actors/writers/directors.
    """
    query = all_persons_query(size=size)
    resp = await search.search(index="movies", body=query)
    return parse_persons_from_agg(resp)

async def fetch_persons_paginated(search, page: int, size: int) -> List[Person]:
    all_persons = await fetch_persons_list(search)
    return Paginator.paginate(all_persons, page, size, Person)

async def fetch_person_by_id(self, person_uuid: UUID) -> Optional[Person]:
    resp = await self.search_index("movies", person_by_id_query(person_uuid))
    return parse_person_with_films(resp["hits"]["hits"], person_uuid)

async def fetch_person_by_name(self, query_str: str) -> List[Person]:
    resp = await self.search_index("movies", search_person_query(query_str))
    return parse_persons_with_name(resp["hits"]["hits"], query_str)