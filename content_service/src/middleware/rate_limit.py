import time
import uuid
import logging
from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from core.logger import request_id_ctx

logger = logging.getLogger("app")


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_requests: int = 5, window_seconds: int = 10):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds

    async def dispatch(self, request: Request, call_next):
        redis = request.app.state.redis_storage
        client_ip = request.client.host
        key = f"rate_limit:{client_ip}"
        now = int(time.time())

        # чистим старые записи
        await redis.zremrangebyscore(key, 0, now - self.window_seconds)

        # текущий счётчик
        req_count = await redis.zcard(key)
        request_id = request_id_ctx.get()

        if req_count >= self.max_requests:
            logger.warning(
                f"⛔ Rate limit exceeded for {client_ip}: {req_count}/{self.max_requests} [id={request_id}]"
            )
            return JSONResponse(
                {"detail": "Too Many Requests"},
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        # добавляем уникальный элемент в Redis (чтобы счётчик рос)
        member = f"{client_ip}:{uuid.uuid4()}"
        await redis.zadd(key, {member: now})
        await redis.expire(key, self.window_seconds)

        logger.info(
            f"✅ Rate counter for {client_ip} -> {req_count + 1}/{self.max_requests} [id={request_id}]"
        )

        response = await call_next(request)
        return response
