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
async def _check_es():
    url = f"http://{settings.ELASTIC_HOST}:{settings.ELASTIC_PORT}"
    timeout = aiohttp.ClientTimeout(total=3)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(url) as resp:
            # достаточно, чтобы хелсчек вернул 200
            assert resp.status == HTTPStatus.OK


async def wait_for_es():
    logger.info("⏳ Waiting for Elasticsearch at %s:%s ...",
                settings.ELASTIC_HOST, settings.ELASTIC_PORT)
    await _check_es()
    logger.info("✅ ES is ready")


if __name__ == "__main__":
    asyncio.run(wait_for_es())