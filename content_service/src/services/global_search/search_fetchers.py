from typing import Any, Dict

async def fetch_search_all(service, query: str, page:int, size: int) -> Dict[str, Any]:
    """Фетчер для глобального поиска по фильмам, персонам и жанрам"""
    films = await service.film_service.search_films(query,page=page, size=size)
    persons = await service.person_service.search_persons(query)
    genres = await service.genre_service.search_genres(query)

    return {
        "films": films,
        "persons": persons,
        "genres": genres,
    }