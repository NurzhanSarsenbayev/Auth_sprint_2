import asyncio
import functools
import logging
import random
from typing import Callable, Tuple, Optional

logger = logging.getLogger(__name__)


def async_retry(
    exceptions: Tuple[type, ...] = (Exception,),
    max_attempts: int = 40,
    base_delay: float = 0.25,
    max_delay: float = 3.0,
    jitter: bool = True,
):
    """Декоратор для ретрая асинхронных функций с экспоненциальным бэкоффом и джиттером."""
    def decorator(func: Callable):
        if not asyncio.iscoroutinefunction(func):
            raise RuntimeError("async_retry supports only async functions")

        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            attempt = 0
            while True:
                try:
                    return await func(*args, **kwargs)
                except asyncio.CancelledError:
                    raise
                except exceptions as exc:
                    attempt += 1
                    if attempt >= max_attempts:
                        logger.exception("Max attempts reached for %s", func.__name__)
                        raise
                    delay = min(max_delay, base_delay * (2 ** (attempt - 1)))
                    if jitter:
                        delay = random.uniform(0, delay)
                    logger.warning(
                        "Retry %s attempt %d/%d in %.2fs due to: %s",
                        func.__name__, attempt, max_attempts, delay, exc
                    )
                    await asyncio.sleep(delay)
        return wrapper
    return decorator