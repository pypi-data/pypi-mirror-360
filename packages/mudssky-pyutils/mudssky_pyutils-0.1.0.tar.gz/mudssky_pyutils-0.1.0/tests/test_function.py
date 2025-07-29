#!/usr/bin/env python

"""Tests for function module."""

import asyncio
import time

import pytest

from pyutils.function import (
    Debouncer,
    Throttler,
    create_polling,
    debounce,
    memoize,
    once,
    throttle,
    with_retry,
)


class TestMemoize:
    """Test memoize decorator."""

    def test_memoize_basic(self):
        """Test basic memoization."""
        call_count = 0

        @memoize
        def expensive_func(x):
            nonlocal call_count
            call_count += 1
            return x * 2

        # First call
        result1 = expensive_func(5)
        assert result1 == 10
        assert call_count == 1

        # Second call with same args - should use cache
        result2 = expensive_func(5)
        assert result2 == 10
        assert call_count == 1  # No additional call

        # Call with different args
        result3 = expensive_func(3)
        assert result3 == 6
        assert call_count == 2

    def test_memoize_with_kwargs(self):
        """Test memoization with keyword arguments."""
        call_count = 0

        @memoize
        def func_with_kwargs(x, y=1):
            nonlocal call_count
            call_count += 1
            return x + y

        result1 = func_with_kwargs(5, y=2)
        assert result1 == 7
        assert call_count == 1

        result2 = func_with_kwargs(5, y=2)
        assert result2 == 7
        assert call_count == 1  # Cached

        result3 = func_with_kwargs(5, y=3)
        assert result3 == 8
        assert call_count == 2  # Different kwargs

    def test_memoize_cache_clear(self):
        """Test cache clearing functionality."""
        call_count = 0

        @memoize
        def func(x):
            nonlocal call_count
            call_count += 1
            return x

        func(1)
        assert call_count == 1

        func(1)
        assert call_count == 1  # Cached

        func.cache_clear()
        func(1)
        assert call_count == 2  # Cache cleared, function called again


class TestOnce:
    """Test once decorator."""

    def test_once_basic(self):
        """Test basic once functionality."""
        call_count = 0

        @once
        def init_func():
            nonlocal call_count
            call_count += 1
            return "initialized"

        result1 = init_func()
        assert result1 == "initialized"
        assert call_count == 1

        result2 = init_func()
        assert result2 == "initialized"
        assert call_count == 1  # Not called again

    def test_once_with_args(self):
        """Test once with arguments."""
        call_count = 0

        @once
        def func_with_args(x, y):
            nonlocal call_count
            call_count += 1
            return x + y

        result1 = func_with_args(1, 2)
        assert result1 == 3
        assert call_count == 1

        # Even with different args, function is not called again
        result2 = func_with_args(5, 6)
        assert result2 == 3  # Returns first result
        assert call_count == 1


class TestDebounce:
    """Test debounce functionality."""

    def test_debounce_basic(self):
        """Test basic debouncing."""
        call_count = 0
        results = []

        @debounce(wait=0.1, trailing=True)
        def debounced_func(value):
            nonlocal call_count
            call_count += 1
            results.append(value)
            return value

        # Rapid calls
        debounced_func("first")
        debounced_func("second")
        debounced_func("third")

        # Wait for debounce to trigger
        time.sleep(0.15)

        # Only the last call should have executed
        assert call_count == 1
        assert results == ["third"]

    def test_debounce_leading(self):
        """Test debouncing with leading edge."""
        call_count = 0
        results = []

        @debounce(wait=0.1, leading=True, trailing=False)
        def debounced_func(value):
            nonlocal call_count
            call_count += 1
            results.append(value)
            return value

        # First call should execute immediately
        debounced_func("first")
        assert call_count == 1
        assert results == ["first"]

        # Subsequent calls within wait period should be ignored
        debounced_func("second")
        debounced_func("third")

        time.sleep(0.15)
        assert call_count == 1
        assert results == ["first"]

    def test_debounce_cancel(self):
        """Test debounce cancellation."""
        call_count = 0

        @debounce(wait=0.1)
        def debounced_func():
            nonlocal call_count
            call_count += 1

        debounced_func()
        debounced_func.cancel()

        time.sleep(0.15)
        assert call_count == 0  # Should not have executed

    def test_debounce_flush(self):
        """Test debounce flush."""
        call_count = 0

        @debounce(wait=0.1)
        def debounced_func(value):
            nonlocal call_count
            call_count += 1
            return value

        debounced_func("test")
        result = debounced_func.flush()

        assert call_count == 1
        assert result == "test"

    def test_debounce_pending(self):
        """Test debounce pending status."""

        @debounce(wait=0.1)
        def debounced_func():
            pass

        assert not debounced_func.pending()

        debounced_func()
        assert debounced_func.pending()

        time.sleep(0.15)
        assert not debounced_func.pending()


class TestThrottle:
    """Test throttle functionality."""

    def test_throttle_basic(self):
        """Test basic throttling."""
        call_count = 0

        @throttle(wait=0.1, leading=True, trailing=False)
        def throttled_func():
            nonlocal call_count
            call_count += 1

        # First call should execute immediately
        throttled_func()
        assert call_count == 1

        # Subsequent calls within wait period should be ignored
        throttled_func()
        throttled_func()
        assert call_count == 1

        # Wait for throttle period to end
        time.sleep(0.15)
        throttled_func()
        # After waiting, the next call should execute
        assert call_count == 2

    def test_throttle_trailing(self):
        """Test throttling with trailing edge."""
        call_count = 0

        @throttle(wait=0.1, leading=False, trailing=True)
        def throttled_func():
            nonlocal call_count
            call_count += 1

        throttled_func()
        throttled_func()

        # Should not execute immediately
        assert call_count == 0

        # Wait for trailing execution
        time.sleep(0.15)
        assert call_count == 1

    def test_throttle_cancel(self):
        """Test throttle cancellation."""
        call_count = 0

        @throttle(wait=0.1, trailing=True)
        def throttled_func():
            nonlocal call_count
            call_count += 1

        throttled_func()
        throttled_func.cancel()

        time.sleep(0.15)
        assert call_count == 0

    def test_throttle_flush(self):
        """Test throttle flush."""
        call_count = 0

        @throttle(wait=0.1)
        def throttled_func():
            nonlocal call_count
            call_count += 1
            return "result"

        throttled_func()
        result = throttled_func.flush()

        assert call_count == 1
        assert result == "result"


class TestWithRetry:
    """Test with_retry decorator."""

    def test_retry_success_on_first_try(self):
        """Test successful execution on first try."""
        call_count = 0

        @with_retry(max_retries=3)
        def reliable_func():
            nonlocal call_count
            call_count += 1
            return "success"

        result = reliable_func()
        assert result == "success"
        assert call_count == 1

    def test_retry_success_after_failures(self):
        """Test successful execution after some failures."""
        call_count = 0

        @with_retry(max_retries=3, delay=0.01)
        def unreliable_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("Temporary failure")
            return "success"

        result = unreliable_func()
        assert result == "success"
        assert call_count == 3

    def test_retry_max_retries_exceeded(self):
        """Test failure when max retries exceeded."""
        call_count = 0

        @with_retry(max_retries=2, delay=0.01)
        def failing_func():
            nonlocal call_count
            call_count += 1
            raise ValueError("Always fails")

        with pytest.raises(ValueError, match="Always fails"):
            failing_func()

        assert call_count == 3  # Initial call + 2 retries

    def test_retry_with_should_retry_condition(self):
        """Test retry with custom should_retry condition."""
        call_count = 0

        @with_retry(max_retries=3, should_retry=lambda e: isinstance(e, ValueError))
        def func_with_different_errors():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise ValueError("Retryable error")
            elif call_count == 2:
                raise TypeError("Non-retryable error")
            return "success"

        with pytest.raises(TypeError, match="Non-retryable error"):
            func_with_different_errors()

        assert call_count == 2  # Should stop on TypeError

    @pytest.mark.asyncio
    async def test_retry_async_function(self):
        """Test retry with async function."""
        call_count = 0

        @with_retry(max_retries=2, delay=0.01)
        async def async_unreliable_func():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ValueError("Async failure")
            return "async success"

        result = await async_unreliable_func()
        assert result == "async success"
        assert call_count == 2


class TestPollingController:
    """Test PollingController and create_polling."""

    @pytest.mark.asyncio
    async def test_polling_basic(self):
        """Test basic polling functionality."""
        call_count = 0

        async def task():
            nonlocal call_count
            call_count += 1
            return {"count": call_count}

        controller = create_polling(
            task=task, interval=0.01, max_executions=3, immediate=True
        )

        await controller.start()

        # Wait a bit to ensure polling completes
        await asyncio.sleep(0.1)

        status = controller.status()
        assert status["execution_count"] == 3
        assert call_count == 3
        # Controller should be stopped after reaching max_executions
        assert status["status"] == "stopped"

    @pytest.mark.asyncio
    async def test_polling_with_stop_condition(self):
        """Test polling with stop condition."""
        call_count = 0

        async def task():
            nonlocal call_count
            call_count += 1
            return {"done": call_count >= 2}

        controller = create_polling(
            task=task,
            stop_condition=lambda result: result["done"],
            interval=0.01,
            immediate=True,
        )

        await controller.start()

        status = controller.status()
        assert status["execution_count"] == 2
        assert call_count == 2

    @pytest.mark.asyncio
    async def test_polling_with_error_handling(self):
        """Test polling with error handling."""
        call_count = 0
        error_count = 0

        async def task():
            nonlocal call_count
            call_count += 1
            if call_count <= 2:
                raise ValueError("Temporary error")
            return {"success": True}

        def error_handler(error):
            nonlocal error_count
            error_count += 1

        controller = create_polling(
            task=task,
            error_action=error_handler,
            quit_on_error=False,
            interval=0.01,
            max_executions=5,
            immediate=True,
        )

        await controller.start()

        status = controller.status()
        assert error_count == 2  # Two errors handled
        # The controller will continue polling until max_executions is reached
        # since quit_on_error=False, it will keep trying
        assert status["execution_count"] >= 1  # At least one successful execution
        assert call_count >= 3  # At least 3 attempts (2 failures + 1 success)

    @pytest.mark.asyncio
    async def test_polling_stop_manually(self):
        """Test manually stopping polling."""
        call_count = 0

        async def task():
            nonlocal call_count
            call_count += 1
            return {"count": call_count}

        controller = create_polling(task=task, interval=0.01, immediate=True)

        # Start polling in background
        polling_task = asyncio.create_task(controller.start())

        # Let it run a bit
        await asyncio.sleep(0.05)

        # Stop manually
        controller.stop()

        # Wait for task to complete
        await polling_task

        assert call_count > 0
        status = controller.status()
        assert status["status"] == "stopped"

    @pytest.mark.asyncio
    async def test_polling_with_progress_callback(self):
        """Test polling with progress callback."""
        call_count = 0
        progress_calls = []

        async def task():
            nonlocal call_count
            call_count += 1
            return {"step": call_count}

        def on_progress(result):
            progress_calls.append(result)

        controller = create_polling(
            task=task,
            on_progress=on_progress,
            interval=0.01,
            max_executions=3,
            immediate=True,
        )

        await controller.start()

        assert len(progress_calls) == 3
        assert progress_calls[0]["step"] == 1
        assert progress_calls[1]["step"] == 2
        assert progress_calls[2]["step"] == 3


class TestDebouncer:
    """Test Debouncer class directly."""

    def test_debouncer_init(self):
        """Test Debouncer initialization."""

        def test_func():
            return "test"

        debouncer = Debouncer(test_func, wait=0.5, leading=True, trailing=False)

        assert debouncer.func == test_func
        assert debouncer.wait == 0.5
        assert debouncer.leading is True
        assert debouncer.trailing is False

    def test_debouncer_call(self):
        """Test Debouncer call functionality."""
        call_count = 0

        def test_func(value):
            nonlocal call_count
            call_count += 1
            return value

        debouncer = Debouncer(test_func, wait=0.1, trailing=True)

        debouncer("test1")
        debouncer("test2")

        time.sleep(0.15)
        assert call_count == 1


class TestThrottler:
    """Test Throttler class directly."""

    def test_throttler_init(self):
        """Test Throttler initialization."""

        def test_func():
            return "test"

        throttler = Throttler(test_func, wait=0.5, leading=False, trailing=True)

        assert throttler.func == test_func
        assert throttler.wait == 0.5
        assert throttler.leading is False
        assert throttler.trailing is True

    def test_throttler_call(self):
        """Test Throttler call functionality."""
        call_count = 0

        def test_func():
            nonlocal call_count
            call_count += 1

        throttler = Throttler(test_func, wait=0.1, leading=True)

        throttler()
        assert call_count == 1

        throttler()
        throttler()
        assert call_count == 1  # Should not increase due to throttling
