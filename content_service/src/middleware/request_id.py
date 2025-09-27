import uuid
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from core.logger import request_id_ctx

logger = logging.getLogger("app")

class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # Берём X-Request-ID из заголовка или генерим новый
        request_id = request.headers.get("x-request-id", str(uuid.uuid4()))
        request_id_ctx.set(request_id)

        logger.info(f"➡️ Request {request.method} {request.url.path} [id={request_id}]")
        response = await call_next(request)
        logger.info(f"⬅️ Response {response.status_code} [id={request_id}]")

        # Проставляем обратно в заголовки
        response.headers["x-request-id"] = request_id
        return response
