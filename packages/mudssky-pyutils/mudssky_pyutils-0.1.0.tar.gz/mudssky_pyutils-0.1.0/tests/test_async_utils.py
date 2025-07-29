#!/usr/bin/env python

"""Tests for async_utils module."""

import asyncio
import time

import pytest

from pyutils.async_utils import (
    AsyncTimer,
    batch_process,
    delay,
    filter_async,
    gather_with_concurrency,
    map_async,
    race,
    retry_async,
    run_in_thread,
    sleep_async,
    timeout,
    wait_for_all,
    wait_for_any,
    with_timeout_default,
)


class TestSleepAsync:
    """Test sleep_async function."""

    @pytest.mark.asyncio
    async def test_sleep_async_basic(self):
        """Test basic sleep functionality."""
        start_time = time.time()
        await sleep_async(0.1)
        elapsed = time.time() - start_time

        assert elapsed >= 0.1
        assert elapsed < 0.2  # Should not take too much longer

    @pytest.mark.asyncio
    async def test_sleep_async_zero(self):
        """Test sleep with zero seconds."""
        start_time = time.time()
        await sleep_async(0)
        elapsed = time.time() - start_time

        assert elapsed < 0.01  # Should be very quick


class TestTimeout:
    """Test timeout function."""

    @pytest.mark.asyncio
    async def test_timeout_success(self):
        """Test timeout with successful completion."""

        async def quick_task():
            await asyncio.sleep(0.05)
            return "success"

        result = await timeout(quick_task(), 0.2)
        assert result == "success"

    @pytest.mark.asyncio
    async def test_timeout_with_default(self):
        """Test timeout with default value."""

        async def slow_task():
            await asyncio.sleep(0.2)
            return "success"

        result = await timeout(slow_task(), 0.05, "default")
        assert result == "default"

    @pytest.mark.asyncio
    async def test_timeout_raises_exception(self):
        """Test timeout raises exception when no default."""

        async def slow_task():
            await asyncio.sleep(0.2)
            return "success"

        with pytest.raises(asyncio.TimeoutError):
            await timeout(slow_task(), 0.05)


class TestDelay:
    """Test delay function."""

    @pytest.mark.asyncio
    async def test_delay_basic(self):
        """Test basic delay functionality."""
        start_time = time.time()
        result = await delay("test_value", 0.1)
        elapsed = time.time() - start_time

        assert result == "test_value"
        assert elapsed >= 0.1
        assert elapsed < 0.2  # Should not take too much longer

    @pytest.mark.asyncio
    async def test_delay_zero_seconds(self):
        """Test delay with zero seconds."""
        start_time = time.time()
        result = await delay(42, 0)
        elapsed = time.time() - start_time

        assert result == 42
        assert elapsed < 0.01  # Should be very quick

    @pytest.mark.asyncio
    async def test_delay_none_value(self):
        """Test delay with None value."""
        result = await delay(None, 0.05)
        assert result is None

    @pytest.mark.asyncio
    async def test_delay_complex_object(self):
        """Test delay with complex object."""
        test_obj = {"a": 1, "b": [2, 3, 4]}
        result = await delay(test_obj, 0.05)
        assert result == test_obj
        assert result is test_obj  # Should be same reference


class TestGatherWithConcurrency:
    """Test gather_with_concurrency function."""

    @pytest.mark.asyncio
    async def test_gather_with_concurrency_basic(self):
        """Test basic concurrent gathering."""

        async def task(value):
            await asyncio.sleep(0.05)
            return value * 2

        tasks = [task(i) for i in range(5)]
        results = await gather_with_concurrency(*tasks, limit=2)

        assert results == [0, 2, 4, 6, 8]

    @pytest.mark.asyncio
    async def test_gather_with_concurrency_preserves_order(self):
        """Test that results are returned in original order."""

        async def task(value):
            # Reverse delay to test order preservation
            await asyncio.sleep(0.1 - value * 0.01)
            return value

        tasks = [task(i) for i in range(5)]
        results = await gather_with_concurrency(*tasks, limit=10)

        assert results == [0, 1, 2, 3, 4]

    @pytest.mark.asyncio
    async def test_gather_with_concurrency_empty(self):
        """Test gathering with no tasks."""
        results = await gather_with_concurrency(limit=2)
        assert results == []


class TestRace:
    """Test race function."""

    @pytest.mark.asyncio
    async def test_race_first_wins(self):
        """Test race where first coroutine completes first."""

        async def fast():
            await asyncio.sleep(0.05)
            return "fast"

        async def slow():
            await asyncio.sleep(0.2)
            return "slow"

        result = await race(fast(), slow())
        assert result == "fast"

    @pytest.mark.asyncio
    async def test_race_second_wins(self):
        """Test race where second coroutine completes first."""

        async def slow():
            await asyncio.sleep(0.2)
            return "slow"

        async def fast():
            await asyncio.sleep(0.05)
            return "fast"

        result = await race(slow(), fast())
        assert result == "fast"

    @pytest.mark.asyncio
    async def test_race_single_coroutine(self):
        """Test race with single coroutine."""

        async def single():
            return "only_one"

        result = await race(single())
        assert result == "only_one"


class TestRetryAsync:
    """Test retry_async function."""

    @pytest.mark.asyncio
    async def test_retry_async_success_first_try(self):
        """Test retry when function succeeds on first try."""
        call_count = 0

        async def successful_func():
            nonlocal call_count
            call_count += 1
            return "success"

        result = await retry_async(successful_func, max_retries=3)
        assert result == "success"
        assert call_count == 1

    @pytest.mark.asyncio
    async def test_retry_async_success_after_retries(self):
        """Test retry when function succeeds after some failures."""
        call_count = 0

        async def flaky_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("Temporary error")
            return "success"

        result = await retry_async(flaky_func, max_retries=3, delay=0.01)
        assert result == "success"
        assert call_count == 3

    @pytest.mark.asyncio
    async def test_retry_async_all_retries_fail(self):
        """Test retry when all attempts fail."""
        call_count = 0

        async def failing_func():
            nonlocal call_count
            call_count += 1
            raise ValueError(f"Error on attempt {call_count}")

        with pytest.raises(ValueError, match="Error on attempt 4"):
            await retry_async(failing_func, max_retries=3, delay=0.01)

        assert call_count == 4  # Initial attempt + 3 retries

    @pytest.mark.asyncio
    async def test_retry_async_with_should_retry(self):
        """Test retry with custom should_retry function."""
        call_count = 0

        async def func_with_different_errors():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise ValueError("Retryable error")
            elif call_count == 2:
                raise TypeError("Non-retryable error")
            return "success"

        def should_retry(error):
            return isinstance(error, ValueError)

        with pytest.raises(TypeError, match="Non-retryable error"):
            await retry_async(
                func_with_different_errors,
                max_retries=3,
                delay=0.01,
                should_retry=should_retry,
            )

        assert call_count == 2


class TestMapAsync:
    """Test map_async function."""

    @pytest.mark.asyncio
    async def test_map_async_basic(self):
        """Test basic async mapping."""

        async def double(x):
            await asyncio.sleep(0.01)
            return x * 2

        items = [1, 2, 3, 4, 5]
        result = await map_async(double, items)

        assert result == [2, 4, 6, 8, 10]

    @pytest.mark.asyncio
    async def test_map_async_empty_list(self):
        """Test async mapping with empty list."""

        async def double(x):
            return x * 2

        result = await map_async(double, [])
        assert result == []

    @pytest.mark.asyncio
    async def test_map_async_with_strings(self):
        """Test async mapping with strings."""

        async def upper_with_delay(s):
            await asyncio.sleep(0.01)
            return s.upper()

        items = ["hello", "world", "test"]
        result = await map_async(upper_with_delay, items)

        assert result == ["HELLO", "WORLD", "TEST"]

    @pytest.mark.asyncio
    async def test_map_async_preserves_order(self):
        """Test that async mapping preserves order even with different delays."""

        async def delayed_identity(x):
            # Longer delay for smaller numbers to test order preservation
            delay_time = 0.05 - (x * 0.005)
            await asyncio.sleep(delay_time)
            return x

        items = [1, 2, 3, 4, 5]
        result = await map_async(delayed_identity, items)

        assert result == [1, 2, 3, 4, 5]

    @pytest.mark.asyncio
    async def test_map_async_with_concurrency(self):
        """Test async mapping with concurrency limit."""

        async def slow_double(x):
            await asyncio.sleep(0.05)
            return x * 2

        items = [1, 2, 3, 4]
        start_time = time.time()
        result = await map_async(slow_double, items, concurrency=2)
        elapsed = time.time() - start_time

        assert result == [2, 4, 6, 8]
        # With concurrency=2, should take about 0.1s (2 batches of 0.05s each)
        assert elapsed >= 0.1
        assert elapsed < 0.15


class TestFilterAsync:
    """Test filter_async function."""

    @pytest.mark.asyncio
    async def test_filter_async_basic(self):
        """Test basic async filtering."""

        async def is_even(x):
            await asyncio.sleep(0.01)
            return x % 2 == 0

        items = [1, 2, 3, 4, 5, 6]
        result = await filter_async(is_even, items)

        assert result == [2, 4, 6]

    @pytest.mark.asyncio
    async def test_filter_async_empty_list(self):
        """Test async filtering with empty list."""

        async def always_true(x):
            return True

        result = await filter_async(always_true, [])
        assert result == []

    @pytest.mark.asyncio
    async def test_filter_async_none_match(self):
        """Test async filtering where no items match."""

        async def always_false(x):
            await asyncio.sleep(0.01)
            return False

        items = [1, 2, 3, 4, 5]
        result = await filter_async(always_false, items)

        assert result == []

    @pytest.mark.asyncio
    async def test_filter_async_all_match(self):
        """Test async filtering where all items match."""

        async def always_true(x):
            await asyncio.sleep(0.01)
            return True

        items = [1, 2, 3, 4, 5]
        result = await filter_async(always_true, items)

        assert result == [1, 2, 3, 4, 5]


class TestRunInThread:
    """Test run_in_thread function."""

    @pytest.mark.asyncio
    async def test_run_in_thread_basic(self):
        """Test running sync function in thread."""

        def sync_function(x, y):
            return x + y

        result = await run_in_thread(sync_function, 5, 3)
        assert result == 8

    @pytest.mark.asyncio
    async def test_run_in_thread_with_kwargs(self):
        """Test running sync function with keyword arguments."""

        def sync_function(x, y=10):
            return x * y

        result = await run_in_thread(sync_function, 5, y=3)
        assert result == 15

    @pytest.mark.asyncio
    async def test_run_in_thread_cpu_intensive(self):
        """Test running CPU-intensive task in thread."""

        def cpu_task(n):
            return sum(i * i for i in range(n))

        result = await run_in_thread(cpu_task, 100)
        expected = sum(i * i for i in range(100))
        assert result == expected


class TestBatchProcess:
    """Test batch_process function."""

    @pytest.mark.asyncio
    async def test_batch_process_basic(self):
        """Test basic batch processing."""

        async def process_batch(batch):
            await asyncio.sleep(0.01)
            return [item * 2 for item in batch]

        items = list(range(10))
        result = await batch_process(items, process_batch, batch_size=3)

        expected = [i * 2 for i in range(10)]
        assert result == expected

    @pytest.mark.asyncio
    async def test_batch_process_empty_list(self):
        """Test batch processing with empty list."""

        async def process_batch(batch):
            return [item * 2 for item in batch]

        result = await batch_process([], process_batch, batch_size=3)
        assert result == []

    @pytest.mark.asyncio
    async def test_batch_process_single_batch(self):
        """Test batch processing with single batch."""

        async def process_batch(batch):
            await asyncio.sleep(0.01)
            return [item + 10 for item in batch]

        items = [1, 2, 3]
        result = await batch_process(items, process_batch, batch_size=5)

        assert result == [11, 12, 13]


class TestAsyncTimer:
    """Test AsyncTimer context manager."""

    @pytest.mark.asyncio
    async def test_async_timer_basic(self):
        """Test basic timer functionality."""
        async with AsyncTimer() as timer:
            await asyncio.sleep(0.1)

        assert timer.elapsed is not None
        assert timer.elapsed >= 0.1
        assert timer.elapsed < 0.2
        assert timer.start_time is not None
        assert timer.end_time is not None

    @pytest.mark.asyncio
    async def test_async_timer_zero_time(self):
        """Test timer with minimal time."""
        async with AsyncTimer() as timer:
            pass  # No delay

        assert timer.elapsed is not None
        assert timer.elapsed >= 0
        assert timer.elapsed < 0.01


class TestWithTimeoutDefault:
    """Test with_timeout_default function."""

    @pytest.mark.asyncio
    async def test_with_timeout_default_success(self):
        """Test timeout with successful completion."""

        async def quick_task():
            await asyncio.sleep(0.05)
            return "success"

        result = await with_timeout_default(quick_task(), 0.2, "default")
        assert result == "success"

    @pytest.mark.asyncio
    async def test_with_timeout_default_timeout(self):
        """Test timeout returns default value."""

        async def slow_task():
            await asyncio.sleep(0.2)
            return "success"

        result = await with_timeout_default(slow_task(), 0.05, "default")
        assert result == "default"


class TestWaitForAll:
    """Test wait_for_all function."""

    @pytest.mark.asyncio
    async def test_wait_for_all_basic(self):
        """Test waiting for all coroutines."""

        async def task1():
            await asyncio.sleep(0.05)
            return "task1"

        async def task2():
            await asyncio.sleep(0.1)
            return "task2"

        results = await wait_for_all(task1(), task2())
        assert results == ["task1", "task2"]

    @pytest.mark.asyncio
    async def test_wait_for_all_with_timeout(self):
        """Test waiting for all with timeout."""

        async def quick_task():
            await asyncio.sleep(0.05)
            return "quick"

        async def slow_task():
            await asyncio.sleep(0.2)
            return "slow"

        with pytest.raises(asyncio.TimeoutError):
            await wait_for_all(quick_task(), slow_task(), timeout=0.1)


class TestWaitForAny:
    """Test wait_for_any function."""

    @pytest.mark.asyncio
    async def test_wait_for_any_basic(self):
        """Test waiting for any coroutine."""

        async def fast_task():
            await asyncio.sleep(0.05)
            return "fast"

        async def slow_task():
            await asyncio.sleep(0.2)
            return "slow"

        result = await wait_for_any(fast_task(), slow_task())
        assert result == "fast"

    @pytest.mark.asyncio
    async def test_wait_for_any_with_timeout(self):
        """Test waiting for any with timeout."""

        async def slow_task1():
            await asyncio.sleep(0.2)
            return "slow1"

        async def slow_task2():
            await asyncio.sleep(0.3)
            return "slow2"

        with pytest.raises(asyncio.TimeoutError):
            await wait_for_any(slow_task1(), slow_task2(), timeout=0.1)
