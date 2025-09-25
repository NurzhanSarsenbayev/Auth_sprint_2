import asyncio
from contextlib import asynccontextmanager

from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from redis.asyncio import Redis

from api.v1 import films,genres,persons,search
from core.config import settings
from services.cache_builder import build_cache, wait_for_elastic


@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- startup ---
    app.state.redis_storage = Redis(host=settings.redis_host, port=settings.redis_port)
    app.state.es_storage = AsyncElasticsearch(
        hosts=[f"http://{settings.elastic_host}:{settings.elastic_port}"]
    )
    # Ждём готовности Elasticsearch
    # await wait_for_elastic(app.state.elastic, timeout=60)
    # await wait_for_index(app.state.elastic, "movies", timeout=60)
    # запускаем кэширование в фоне
    # asyncio.create_task(build_cache(app.state.elastic, app.state.redis))

    yield  # здесь приложение доступно

    # --- shutdown ---
    await app.state.redis_storage.close()
    await app.state.es_storage.close()


app = FastAPI(
    title="Read-only API для онлайн-кинотеатра",
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
    description="Информация о фильмах, жанрах и людях, участвовавших в создании произведения",
    version="1.0.0",
    lifespan=lifespan
)

# Подключаем роутер к серверу, указав префикс /v1/films
# Теги указываем для удобства навигации по документации

app.include_router(
    search.router,
    prefix="/api/v1/search",
    tags=["search"]
)

# Роутер для фильмов
app.include_router(
    films.router,
    prefix="/api/v1/films",
    tags=["films"]
)

# Роутер для жанров
app.include_router(
    genres.router,
    prefix="/api/v1/genres",
    tags=["genres"]
)

# Роутер для персон
app.include_router(
    persons.router,
    prefix="/api/v1/persons",
    tags=["persons"]
)