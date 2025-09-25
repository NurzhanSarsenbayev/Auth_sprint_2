from fastapi import FastAPI
from fastapi_pagination import add_pagination
from contextlib import asynccontextmanager
from api.v1 import auth, users, roles, user_roles
from db.redis_db import init_redis, close_redis
from db.postgres import make_engine, make_session_factory


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

    yield

    # --- Shutdown ---
    await engine.dispose()
    await close_redis(redis)


app = FastAPI(title="Auth Service", lifespan=lifespan)
add_pagination(app)

# Роутеры
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(roles.router, prefix="/api/v1/roles", tags=["roles"])
app.include_router(user_roles.router,
                   prefix="/api/v1/user_roles", tags=["user_roles"])


@app.get("/")
async def root():
    return {"message": "Auth service is running!"}
