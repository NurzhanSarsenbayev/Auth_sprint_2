import asyncio
import logging

import redis.asyncio as redis
from redis.exceptions import ConnectionError as RedisConnectionError

from functional.settings import settings
from functional.utils.backoff import async_retry

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@async_retry(
    exceptions=(RedisConnectionError, AssertionError),
    max_attempts=settings.WAIT_MAX_ATTEMPTS,
    base_delay=settings.WAIT_BASE_DELAY,
    max_delay=settings.WAIT_MAX_DELAY,
)
async def _check_redis():
    client = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)
    pong = await client.ping()
    assert pong is True
    await client.aclose()


async def wait_for_redis():
    logger.info("⏳ Waiting for Redis at %s:%s ...", settings.REDIS_HOST, settings.REDIS_PORT)
    await _check_redis()
    logger.info("✅ Redis is ready")


if __name__ == "__main__":
    asyncio.run(wait_for_redis())