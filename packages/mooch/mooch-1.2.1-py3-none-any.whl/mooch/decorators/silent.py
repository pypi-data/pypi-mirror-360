import logging
from functools import wraps
from typing import Callable


def silent(fallback: object = None, *, log_exceptions: bool = True) -> object:
    """Suppress all exceptions in a function and return fallback value (default: None) if an exception occurs.

    Args:
        fallback (object, optional): The value to return if an exception is raised. Defaults to None.
        log_exceptions (bool, optional): Whether to log exceptions using the standard logging module. Defaults to True.

    Returns:
        object: The result of the decorated function, or the fallback value if an exception occurs.

    Notes:
        - All exceptions are caught and suppressed. (Except BaseExceptions like SystemExit, KeyboardInterrupt, etc.)
        - If log_exceptions is True, exceptions are still logged at the ERROR level.

    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: object, **kwargs: object) -> object:
            try:
                return func(*args, **kwargs)
            except Exception:
                if log_exceptions:
                    logger = logging.getLogger(func.__module__)
                    logger.exception(f"Silent Exception in {func.__name__}. Returning fallback value '{fallback}'.")
                return fallback

        return wrapper

    return decorator
