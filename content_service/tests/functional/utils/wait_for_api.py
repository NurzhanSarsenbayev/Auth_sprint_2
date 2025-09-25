import asyncio
import logging
from http import HTTPStatus

import aiohttp

from functional.settings import settings
from functional.utils.backoff import async_retry

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@async_retry(
    exceptions=(aiohttp.ClientError, asyncio.TimeoutError, AssertionError),
    max_attempts=settings.WAIT_MAX_ATTEMPTS,
    base_delay=settings.WAIT_BASE_DELAY,
    max_delay=settings.WAIT_MAX_DELAY,
)
async def _check_api():
    url = f"http://{settings.API_HOST}:{settings.API_PORT}/api/openapi"
    timeout = aiohttp.ClientTimeout(total=3)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(url) as resp:
            assert resp.status == HTTPStatus.OK


async def wait_for_api():
    logger.info("⏳ Waiting for API at %s:%s ...", settings.API_HOST, settings.API_PORT)
    await _check_api()
    logger.info("✅ API is ready")


if __name__ == "__main__":
    asyncio.run(wait_for_api())