import asyncio
import logging

import pytest

from mooch.decorators.timeit import timeit


def test_timeit_sync_logs_execution_time(caplog):
    @timeit
    def add(a, b):
        return a + b

    with caplog.at_level(logging.DEBUG):
        result = add(2, 3)
    assert result == 5
    assert any("add executed in" in message for message in caplog.messages)


@pytest.mark.asyncio
async def test_timeit_async_logs_execution_time(caplog):
    @timeit
    async def async_add(a, b):
        await asyncio.sleep(0.01)
        return a + b

    with caplog.at_level(logging.DEBUG):
        result = await async_add(4, 6)
    assert result == 10
    assert any("async_add executed in" in message for message in caplog.messages)


def test_timeit_preserves_function_metadata():
    @timeit
    def foo(x):
        """Test docstring."""
        return x

    assert foo.__name__ == "foo"
    assert foo.__doc__ == "Test docstring."


@pytest.mark.asyncio
async def test_timeit_async_preserves_function_metadata():
    @timeit
    async def bar(y):
        """Async docstring."""
        return y

    assert bar.__name__ == "bar"
    assert bar.__doc__ == "Async docstring."
