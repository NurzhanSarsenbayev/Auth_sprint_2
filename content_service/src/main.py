import asyncio
import logging
from contextlib import asynccontextmanager
from logging.config import dictConfig

from api.v1 import films, genres, persons, ping, search
from core.config import settings
from core.logger import LOGGING
from core.telemetry import instrument_app, setup_tracing, shutdown_tracing
from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from middleware.rate_limit import RateLimitMiddleware
from middleware.request_id import RequestIDMiddleware
from redis.asyncio import Redis
from services.cache_builder import wait_for_elastic

# 👇 добавляем импорт для JWKS
from utils.jwt import get_jwks

# --- Логирование ---
dictConfig(LOGGING)
logger = logging.getLogger("app")


async def jwks_refresher(cache: Redis, interval: int = 600):
    """Фоновая задача для периодического обновления JWKS из Auth."""
    logger.info(f"🚀 JWKS refresher запущен, интервал = {interval} сек.")
    while True:
        try:
            jwks = await get_jwks(cache)
            kids = [k.get("kid") for k in jwks.get("keys", [])]
            logger.info(
                "✅ JWKS обновлён, ключей: %s, kids=%s",
                len(kids),
                kids,
            )
        except Exception as e:
            logger.error(f"❌ Ошибка обновления JWKS: {e}")
        finally:
            logger.debug("⏳ Следующее обновление JWKS через %s секунд", interval)
            await asyncio.sleep(interval)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- startup ---
    logger.info("🚀 Запуск Content Service (lifespan.startup)")

    app.state.redis_storage = Redis(host=settings.redis_host, port=settings.redis_port)
    app.state.es_storage = AsyncElasticsearch(
        hosts=[f"http://{settings.elastic_host}:{settings.elastic_port}"]
    )

    # ждём Elastic при старте
    await wait_for_elastic(app.state.es_storage, timeout=60)

    # Запускаем фоновый обновитель JWKS
    task = asyncio.create_task(jwks_refresher(app.state.redis_storage, interval=600))
    app.state.jwks_refresher_task = task
    logger.info("✅ JWKS refresher task started")

    yield  # здесь приложение доступно

    # --- shutdown ---
    logger.info("🛑 Остановка Content Service (lifespan.shutdown)")
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        logger.info("✅ JWKS refresher task cancelled")

    await app.state.redis_storage.close()
    await app.state.es_storage.close()
    logger.info("✅ Redis и Elasticsearch соединения закрыты")

    shutdown_tracing()
    logger.info("✅ OpenTelemetry трассировка корректно остановлена")


# --- Сначала трейсинг ---
if settings.enable_tracer:
    setup_tracing(settings.otel_service_name)
else:
    logger.info("🚫 OpenTelemetry отключён (ENABLE_TRACER=False)")

# --- FastAPI App ---
app = FastAPI(
    title="Read-only API для онлайн-кинотеатра",
    openapi_url="/api/openapi",
    default_response_class=ORJSONResponse,
    description="Информация о фильмах, жанрах и людях, участвовавших в создании произведения",
    version="1.0.0",
    lifespan=lifespan,
)

# --- Инструментируем app ---
instrument_app(app)

# 👇 Middleware
app.add_middleware(RateLimitMiddleware, max_requests=5, window_seconds=10)
app.add_middleware(RequestIDMiddleware)

# --- Роутеры ---
app.include_router(search.router, prefix="/api/v1/search", tags=["search"])
app.include_router(films.router, prefix="/api/v1/films", tags=["films"])
app.include_router(genres.router, prefix="/api/v1/genres", tags=["genres"])
app.include_router(persons.router, prefix="/api/v1/persons", tags=["persons"])
app.include_router(ping.router, prefix="/api/v1/ping", tags=["ping"])
