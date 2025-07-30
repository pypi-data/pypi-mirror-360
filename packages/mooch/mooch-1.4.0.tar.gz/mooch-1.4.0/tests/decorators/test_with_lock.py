import asyncio
import threading
import time

import pytest

from mooch.decorators import with_lock


def test_sync_lock_with_explicit_lock():
    _lock = threading.Lock()
    call_order = []

    @with_lock(_lock)
    def critical_section(x):
        call_order.append(x)
        return x * 2

    @with_lock(_lock)
    def another_critical_section(x):
        call_order.append(x)
        time.sleep(0.05)
        return x + 100

    results = []
    results2 = []

    def worker(val):
        results.append(critical_section(val))

    def worker2(val):
        results2.append(another_critical_section(val))

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(5)]
    threads2 = [threading.Thread(target=worker2, args=(i,)) for i in range(100, 105)]
    for t in threads:
        t.start()
    for t2 in threads2:
        t2.start()
    for t in threads:
        t.join()
    for t in threads + threads2:
        t.join()

    assert results == [i * 2 for i in range(5)]
    assert call_order == [0, 1, 2, 3, 4, 100, 101, 102, 103, 104]


def test_sync_lock_with_no_lock_shares_lock_with_same_function_only():
    call_order = []

    @with_lock()
    def critical_section(x):
        call_order.append(x)
        time.sleep(0.25)
        return x * 5

    @with_lock()
    def another_critical_section(x):
        call_order.append(x)
        time.sleep(0.25)
        return x + 100

    results = []
    results2 = []

    def worker(val):
        results.append(critical_section(val))

    def worker2(val):
        results2.append(another_critical_section(val))

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(5)]
    threads2 = [threading.Thread(target=worker2, args=(i,)) for i in range(100, 105)]

    for t1 in threads:
        t1.start()
    for t2 in threads2:
        t2.start()
    for t in threads + threads2:
        t.join()

    assert results == [i * 5 for i in range(5)]
    for i in range(5):
        assert call_order[i * 2] == i or call_order[i * 2 + 1] == i

    assert results2 == [i + 200 for i in range(5)]


@pytest.mark.asyncio
async def test_async_lock_with_explicit_lock():
    _lock = asyncio.Lock()
    call_order = []

    @with_lock(_lock)
    async def async_critical_section(x):
        call_order.append(x)
        await asyncio.sleep(0.01)
        return x * 3

    async def worker(val, results):
        res = await async_critical_section(val)
        results.append(res)

    results = []
    await asyncio.gather(*(worker(i, results) for i in range(5)))
    assert results == [i * 3 for i in range(5)]
    assert call_order == [0, 1, 2, 3, 4]


@pytest.mark.asyncio
async def test_async_lock_with_default_lock():
    call_count = []

    @with_lock()
    async def increment(x):
        call_count.append(x)
        await asyncio.sleep(0.01)
        return x + 10

    result1 = await increment(5)
    result2 = await increment(7)
    assert result1 == 15
    assert result2 == 17
    assert call_count == [5, 7]
