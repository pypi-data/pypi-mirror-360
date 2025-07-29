import functools
import logging
import time
from typing import Callable


def retry(
    times: int,
    *,
    delay: float = 0.1,
    fallback: object = None,
    fail_on_none: bool = False,
    log_exceptions: bool = True,
) -> Callable:
    """Retry a function call a specified number of times if it raises an exception or (optionally) returns None.

    Args:
        times (int): Number of times to retry the function call.
        delay (float, optional): Delay in seconds between retries. Defaults to 0.1.
        fallback (object, optional): Value to return if all retries fail. Defaults to None.
        fail_on_none (bool, optional): If True, treat a None return value as a failure and retry. Defaults to False.
        log_exceptions (bool, optional): If True, log exceptions on each failure. Defaults to True.

    Returns:
        Callable: A decorator that applies the retry logic to the target function.

    Raises:
        Exception: Re-raises the last exception if all retries fail and no fallback is provided.
        ValueError: If `fail_on_none` is True and the function returns None.

    """

    def decorator(func: callable) -> callable:
        @functools.wraps(func)
        def wrapper(*args: object, **kwargs: object) -> object:
            for i in range(times):
                try:
                    result = func(*args, **kwargs)
                    if result is None and fail_on_none:
                        msg = "Function returned None"
                        raise ValueError(msg)  # noqa: TRY301
                    return result  # noqa: TRY300
                except Exception:
                    if log_exceptions:
                        logger = logging.getLogger(func.__module__)
                        logger.exception(f"Retry #{i + 1} Exception in {func.__name__}")
                    if i + 1 >= times:
                        if fallback is not None:
                            return fallback
                        raise
                time.sleep(delay)
            return None  # only reached if times is 0

        return wrapper

    return decorator
