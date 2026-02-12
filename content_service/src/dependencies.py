import logging

from db.protocols import CacheStorageProtocol, SearchStorageProtocol
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from services.films.films_service import FilmService
from services.genres.genres_service import GenreService
from services.global_search.search_service import SearchService
from services.persons.persons_service import PersonService
from utils.jwt import decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)
logger = logging.getLogger("app")


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
    return FilmService(cache=cache, search=es)


def get_person_service(
    es: SearchStorageProtocol = Depends(get_es_storage),
    cache: CacheStorageProtocol = Depends(get_redis_storage),
) -> PersonService:
    return PersonService(cache=cache, search=es)


def get_genre_service(
    es: SearchStorageProtocol = Depends(get_es_storage),
    cache: CacheStorageProtocol = Depends(get_redis_storage),
) -> GenreService:
    return GenreService(cache=cache, search=es)


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


async def get_current_principal(
    token: str | None = Depends(oauth2_scheme_optional),
    cache: CacheStorageProtocol = Depends(get_redis_storage),
):
    logger.info("👤 principal: вход. Есть ли токен? %s", bool(token))
    if not token:
        logger.info("👤 principal: нет токена → guest")
        return "guest"

    try:
        payload = await decode_token(token, cache)
    except HTTPException as e:
        logger.warning(
            "👤 principal: decode_token поднял HTTPException %s (%s)", e.status_code, e.detail
        )
        if e.status_code == status.HTTP_503_SERVICE_UNAVAILABLE:
            logger.info("👤 principal: graceful fallback на guest (503)")
            return "guest"
        raise

    principal = {
        "user_id": payload.get("sub"),
        "email": payload.get("email"),
        "role": "user",
    }
    logger.info("👤 principal: отдаю пользователя %s", principal)
    return principal
