from fastapi import FastAPI
from fastapi_pagination import add_pagination
from fastapi.openapi.utils import get_openapi
from contextlib import asynccontextmanager
from api.v1 import auth, users, roles, user_roles, oauth, well_known
from db.redis_db import init_redis, close_redis
from db.postgres import make_engine, make_session_factory
from middleware.request_id import RequestIDMiddleware
from middleware.rate_limit import RateLimiterMiddleware, RateRule
from core.logging import setup_logging
from core.config import settings
from core import telemetry
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor


@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- DB ---
    engine = make_engine()
    session_factory = make_session_factory(engine)

    app.state.engine = engine
    app.state.session_factory = session_factory

    # --- Redis ---
    redis = await init_redis()
    app.state.redis = redis

    SQLAlchemyInstrumentor().instrument(engine=engine.sync_engine)

    yield

    # --- Shutdown ---
    await engine.dispose()
    await close_redis(redis)


app = FastAPI(title="Auth Service", lifespan=lifespan)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Auth Service",
        version="1.0.0",
        description="API docs",
        routes=app.routes,
    )
    # добавляем ручную схему BearerAuth
    openapi_schema["components"]["securitySchemes"]["BearerAuth"] = {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT",
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
setup_logging()
if settings.enable_tracer:
    telemetry.setup_tracing("auth_service")
    telemetry.instrument_app(app)
add_pagination(app)
rules = [
    # Регистрация — жёстче
    RateRule(r"^/api/v1/users/signup$", limit=5, window=60),
    # Логин — умеренно
    RateRule(r"^/api/v1/users/login$", limit=10, window=60),
    # Все остальные — дефолт (можно не указывать, просто для примера)
    RateRule(r"^/api/v1/.*",
             limit=settings.rate_limit_max_requests,
             window=settings.rate_limit_window_sec),
]

app.add_middleware(
    RateLimiterMiddleware,
    rules=rules,
    default_limit=settings.rate_limit_max_requests,
    default_window=settings.rate_limit_window_sec,
    whitelist_paths=["/health", "/docs", "/openapi.json"],
)
app.add_middleware(RequestIDMiddleware)


# Роутеры
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(roles.router, prefix="/api/v1/roles", tags=["roles"])
app.include_router(user_roles.router,
                   prefix="/api/v1/user_roles", tags=["user_roles"])
app.include_router(oauth.router, prefix="/api/v1/oauth", tags=["oauth"])
app.include_router(well_known.router)


@app.get("/")
async def root():
    return {"message": "Auth service is running!"}
