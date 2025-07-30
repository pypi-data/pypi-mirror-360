import asyncio
import functools
import logging


def log_entry_exit(func: callable):  # noqa: ANN201
    logger = logging.getLogger(func.__module__)

    @functools.wraps(func)
    def run_func(*args, **kwargs):  # noqa: ANN002, ANN003, ANN202
        logger.debug(f"Entering: {func.__name__} with args={args}, kwargs={kwargs}")
        result = func(*args, **kwargs)
        logger.debug(f"Exiting: {func.__name__}")
        return result

    @functools.wraps(func)
    async def async_run_func(*args, **kwargs):  # noqa: ANN002, ANN003, ANN202
        logger.debug(f"Entering: {func.__name__} with args={args}, kwargs={kwargs}")
        result = await func(*args, **kwargs)
        logger.debug(f"Exiting: {func.__name__}")
        return result

    return async_run_func if asyncio.iscoroutinefunction(func) else run_func
