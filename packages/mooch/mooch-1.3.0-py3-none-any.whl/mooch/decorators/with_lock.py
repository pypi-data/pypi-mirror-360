from __future__ import annotations

import asyncio
import functools
import threading


def with_lock(lock: threading.Lock | None = None):  # noqa: ANN201
    """Ensure a function is executed with provided Lock object.

    Notes:
        - If no lock is provided, a new Lock instance is created.
        - Caution: The created lock is only shared among the same decorated function.

    """

    def decorator(func: callable) -> callable:
        nonlocal lock
        if lock is None:
            lock = asyncio.Lock() if asyncio.iscoroutinefunction(func) else threading.Lock()

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):  # noqa: ANN002, ANN003, ANN202
            with lock:
                return func(*args, **kwargs)

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):  # noqa: ANN002, ANN003, ANN202
            async with lock:
                return await func(*args, **kwargs)

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper

    return decorator
