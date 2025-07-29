import warnings
from functools import wraps


# deprecated is not available in Python < 3.13, so we define our own to support 3.9 - 3.12
def deprecated(reason: str = "") -> callable:
    """Mark functions as deprecated.

    When the decorated function is called, a DeprecationWarning is issued with an optional reason.

    Args:
        reason (str, optional): An optional message to include in the deprecation warning. Defaults to "".

    Returns:
        callable: A decorator that wraps the target function and emits a deprecation warning when called.

    """

    def decorator(func: callable) -> callable:
        @wraps(func)
        def wrapper(*args: object, **kwargs: object) -> object:
            warnings.warn(
                f"{func.__name__} is deprecated. {reason}",
                category=DeprecationWarning,
                stacklevel=2,
            )
            return func(*args, **kwargs)

        return wrapper

    return decorator
