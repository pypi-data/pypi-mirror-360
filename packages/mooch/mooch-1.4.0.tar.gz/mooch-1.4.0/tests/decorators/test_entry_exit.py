import asyncio
import logging

import pytest

from mooch.decorators.logging import log_entry_exit


class DummyLogger:
    def __init__(self):
        self.records = []

    def debug(self, msg):
        self.records.append(msg)

    def addHandler(self, handler):
        # Dummy method to satisfy the logger interface
        pass

    def removeHandler(self, handler):
        # Dummy method to satisfy the logger interface
        pass


@pytest.fixture(autouse=True)
def patch_logger(monkeypatch):
    dummy_logger = DummyLogger()
    monkeypatch.setattr(logging, "getLogger", lambda name=None: dummy_logger)
    return dummy_logger


def test_log_entry_exit_sync(patch_logger):
    calls = []

    @log_entry_exit
    def foo(a, b, c=None):
        calls.append((a, b, c))
        return a + b

    result = foo(1, 2, c=3)
    assert result == 3
    assert calls == [(1, 2, 3)]
    logs = patch_logger.records
    assert logs[0].startswith("Entering: foo with args=(1, 2), kwargs={'c': 3}")
    assert logs[1].startswith("Exiting: foo")


@pytest.mark.asyncio
async def test_log_entry_exit_async(patch_logger):
    calls = []

    @log_entry_exit
    async def baz(a, b):
        calls.append((a, b))
        await asyncio.sleep(0)
        return a * b

    result = await baz(3, 4)
    assert result == 12
    assert calls == [(3, 4)]
    logs = patch_logger.records
    assert logs[0].startswith("Entering: baz with args=(3, 4), kwargs={}")
    assert logs[1].startswith("Exiting: baz")


def test_log_entry_exit_preserves_signature():
    @log_entry_exit
    def foo(a, b):
        return a + b

    assert foo.__name__ == "foo"
    assert foo.__qualname__.endswith("foo")


def test_log_entry_exit_preserves_signature_async():
    @log_entry_exit
    async def foo(a, b):
        return a + b

    assert foo.__name__ == "foo"
    assert foo.__qualname__.endswith("foo")
