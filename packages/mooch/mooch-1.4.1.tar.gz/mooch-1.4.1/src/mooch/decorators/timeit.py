import asyncio
import functools
import logging
import time

logger = logging.getLogger(__name__)


def timeit(func: callable):  # noqa: ANN201
    """Log the execution time of sync or async function."""
    logger = logging.getLogger(func.__module__)

    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):  # noqa: ANN002, ANN003, ANN202
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        duration = end - start
        logger.debug(f"{func.__name__} executed in {duration:.6f} seconds.")
        return result

    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):  # noqa: ANN002, ANN003, ANN202
        start = time.perf_counter()
        result = await func(*args, **kwargs)
        end = time.perf_counter()
        duration = end - start
        logger.debug(f"{func.__name__} executed in {duration:.6f} seconds.")
        return result

    return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
