import asyncio
from contextlib import asynccontextmanager
import logging
from logging.config import dictConfig


from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from redis.asyncio import Redis

from core.config import settings
from core.telemetry import setup_tracing, instrument_app
from core.logger import LOGGING

from api.v1 import films, genres, persons, search

from services.cache_builder import build_cache, wait_for_elastic

from middleware.request_id import RequestIDMiddleware
from middleware.rate_limit import RateLimitMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- startup ---
    app.state.redis_storage = Redis(
        host=settings.redis_host,
        port=settings.redis_port
    )
    app.state.es_storage = AsyncElasticsearch(
        hosts=[f"http://{settings.elastic_host}:{settings.elastic_port}"]
    )

    # пример: можно включить ожидание ES и построение кэша
    # await wait_for_elastic(app.state.es_storage, timeout=60)
    # asyncio.create_task(build_cache(app.state.es_storage, app.state.redis_storage))

    yield  # здесь приложение доступно

    # --- shutdown ---
    await app.state.redis_storage.close()
    await app.state.es_storage.close()


# --- Настройка логирования ---
dictConfig(LOGGING)
logger = logging.getLogger("app")

# --- Сначала трейсинг ---
setup_tracing("content_service")

# --- FastAPI App ---
app = FastAPI(
    title="Read-only API для онлайн-кинотеатра",
    default_response_class=ORJSONResponse,
    description="Информация о фильмах, жанрах и людях, участвовавших в создании произведения",
    version="1.0.0",
    lifespan=lifespan,
)

# --- Инструментируем app ---
instrument_app(app)

# 👇 Добавляем rate limiting
app.add_middleware(RateLimitMiddleware, max_requests=5, window_seconds=10)

# --- RequestID ---
app.add_middleware(RequestIDMiddleware)

# --- Роутеры ---
app.include_router(search.router, prefix="/api/v1/search", tags=["search"])
app.include_router(films.router, prefix="/api/v1/films", tags=["films"])
app.include_router(genres.router, prefix="/api/v1/genres", tags=["genres"])
app.include_router(persons.router, prefix="/api/v1/persons", tags=["persons"])


# --- Пример ручки для проверки логирования ---
@app.get("/ping")
async def ping():
    logger.info("Ping endpoint called")
    return {"msg": "pong"}
