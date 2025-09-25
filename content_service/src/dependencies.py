from fastapi import Depends, Request
from db.protocols import SearchStorageProtocol, CacheStorageProtocol
from services.films.films_service import FilmService
from services.persons.persons_service import PersonService
from services.genres.genres_service import GenreService
from services.global_search.search_service import SearchService

# достаем storages из app.state
def get_es_storage(request: Request) -> SearchStorageProtocol:
    return request.app.state.es_storage

def get_redis_storage(request: Request) -> CacheStorageProtocol:
    return request.app.state.redis_storage

# фабрики сервисов

def get_film_service(
    es: SearchStorageProtocol = Depends(get_es_storage),
    cache: CacheStorageProtocol = Depends(get_redis_storage),
) -> FilmService:
    return FilmService(cache=cache,search=es)


def get_person_service(
    es: SearchStorageProtocol = Depends(get_es_storage),
    cache: CacheStorageProtocol = Depends(get_redis_storage),
) -> PersonService:
    return PersonService(cache=cache,search=es)


def get_genre_service(
    es: SearchStorageProtocol = Depends(get_es_storage),
    cache: CacheStorageProtocol = Depends(get_redis_storage),
) -> GenreService:
    return GenreService(cache=cache,search=es)

def get_search_service(
    es: SearchStorageProtocol = Depends(get_es_storage),
    cache: CacheStorageProtocol = Depends(get_redis_storage),
    film_service: FilmService = Depends(get_film_service),
    person_service: PersonService = Depends(get_person_service),
    genre_service: GenreService = Depends(get_genre_service),
) -> SearchService:
    return SearchService(
        cache=cache,
        search=es,
        film_service=film_service,
        person_service=person_service,
        genre_service=genre_service,
    )