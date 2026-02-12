import logging
import time
import uuid

from core.logger import request_id_ctx
from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("app")


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_requests: int = 5, window_seconds: int = 10):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds

    async def dispatch(self, request: Request, call_next):
        # 🔓 bypass для тестов
        if request.headers.get("X-Test-Bypass-Ratelimit") == "1":
            return await call_next(request)

        redis = request.app.state.redis_storage
        client_ip = request.client.host or "unknown"
        key = f"rate_limit:{client_ip}"
        now = int(time.time() * 1000)  # ⚡ миллисекунды
        window_ms = self.window_seconds * 1000
        request_id = request_id_ctx.get()

        # 🧹 очищаем старые записи
        await redis.zremrangebyscore(key, 0, now - window_ms)

        # добавляем текущий запрос
        member = f"{client_ip}:{uuid.uuid4()}"
        await redis.zadd(key, {member: now})
        await redis.expire(key, self.window_seconds)

        # считаем сколько запросов в окне
        req_count = await redis.zcard(key)
        members = await redis.zrange(key, 0, -1, withscores=True)

        logger.info(
            f"📊 RateLimit: ip={client_ip},"
            f" count={req_count}/{self.max_requests}, "
            f"now={now}, members={members}, [id={request_id}]"
        )

        if req_count > self.max_requests:
            logger.warning(
                f"⛔ Rate limit exceeded for "
                f"{client_ip}: "
                f"{req_count}/{self.max_requests}"
                f" [id={request_id}]"
            )
            return JSONResponse(
                {"detail": "Too Many Requests"},
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        return await call_next(request)
