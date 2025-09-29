from fastapi import Depends, Request,HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from db.protocols import SearchStorageProtocol, CacheStorageProtocol
from services.films.films_service import FilmService
from services.persons.persons_service import PersonService
from services.genres.genres_service import GenreService
from services.global_search.search_service import SearchService
from utils.jwt import decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)

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

async def get_current_principal(
    token: str | None = Depends(oauth2_scheme_optional),
    cache: CacheStorageProtocol = Depends(get_redis_storage),
):
    print("👉 TOKEN:", token)

    if not token:
        print("⚠️ Нет токена, возвращаем guest")
        return {"role": "guest"}

    try:
        payload = await decode_token(token, cache)
        print("✅ Декод успешен:", payload)
    except HTTPException as e:
        print(f"❌ Ошибка валидации токена: {e.detail} (status={e.status_code})")
        # fallback на guest
        if e.status_code in (
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_503_SERVICE_UNAVAILABLE,
        ):
            return {"role": "guest"}
        # остальные ошибки пробрасываем
        raise
    except Exception as e:
        # на случай неожиданных ошибок
        import traceback
        print("💥 Неожиданная ошибка при обработке токена:", repr(e))
        print(traceback.format_exc())
        return {"role": "guest"}

    return {
        "user_id": payload.get("sub"),
        "email": payload.get("email"),
        "role": "user",
    }
