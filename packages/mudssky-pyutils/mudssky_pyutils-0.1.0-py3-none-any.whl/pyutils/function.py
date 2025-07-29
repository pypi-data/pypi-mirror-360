"""Function utility functions.

This module provides utility functions for working with functions,
including debounce, throttle, retry mechanisms, and polling,
ported from the jsutils library.
"""

import asyncio
import threading
import time
from collections.abc import Awaitable, Callable
from functools import wraps
from typing import Any, TypeVar


T = TypeVar("T")
F = TypeVar("F", bound=Callable[..., Any])


class Debouncer:
    """Debounce function calls.

    A debounced function will only execute after it hasn't been called
    for a specified wait time.
    """

    def __init__(
        self,
        func: Callable[..., Any],
        wait: float = 0.2,
        leading: bool = False,
        trailing: bool = True,
    ):
        """Initialize debouncer.

        Args:
            func: Function to debounce
            wait: Wait time in seconds, defaults to 0.2
            leading: Execute on leading edge, defaults to False
            trailing: Execute on trailing edge, defaults to True
        """
        self.func = func
        self.wait = wait
        self.leading = leading
        self.trailing = trailing
        self.timer: threading.Timer | None = None
        self.last_args: tuple[Any, ...] = ()
        self.last_kwargs: dict[str, Any] = {}
        self.result: Any = None
        self.is_leading_executed = False
        self.is_trailing_executed = False
        self.lock = threading.Lock()

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """Call the debounced function."""
        with self.lock:
            self.last_args = args
            self.last_kwargs = kwargs

            if self.timer is None:
                if self.leading and not self.is_leading_executed:
                    self.result = self.func(*args, **kwargs)
                    self.is_leading_executed = True

                if not self.leading and not self.trailing and self.is_trailing_executed:
                    self.result = self.func(*args, **kwargs)
                    self.is_trailing_executed = False

                self.timer = threading.Timer(self.wait, self._on_timeout)
                self.timer.start()
            else:
                self.timer.cancel()
                self.timer = threading.Timer(self.wait, self._on_timeout)
                self.timer.start()

            return self.result

    def _on_timeout(self) -> None:
        """Handle timeout event."""
        with self.lock:
            if self.trailing:
                self.result = self.func(*self.last_args, **self.last_kwargs)

            self.is_leading_executed = False
            self.is_trailing_executed = True
            self.timer = None

    def cancel(self) -> None:
        """Cancel pending function call."""
        with self.lock:
            if self.timer:
                self.timer.cancel()
                self.timer = None
            self.is_leading_executed = False
            self.is_trailing_executed = False

    def pending(self) -> bool:
        """Check if function call is pending."""
        with self.lock:
            return self.timer is not None

    def flush(self) -> Any:
        """Immediately execute pending function call."""
        with self.lock:
            if self.timer is None:
                return self.result

            self.timer.cancel()
            self.timer = None
            self.is_leading_executed = False
            self.is_trailing_executed = False
            self.result = self.func(*self.last_args, **self.last_kwargs)
            return self.result


def debounce(
    wait: float = 0.2, leading: bool = False, trailing: bool = True
) -> Callable[[F], Debouncer]:
    """Decorator to debounce function calls.

    Args:
        wait: Wait time in seconds, defaults to 0.2
        leading: Execute on leading edge, defaults to False
        trailing: Execute on trailing edge, defaults to True

    Returns:
        Debounced function

    Examples:
        >>> @debounce(wait=0.1)
        ... def save_data(data):
        ...     print(f"Saving {data}")
        >>>
        >>> save_data("test1")
        >>> save_data("test2")  # Only this will execute after 0.1s
    """

    def decorator(func: F) -> Debouncer:
        return Debouncer(func, wait, leading, trailing)

    return decorator


class Throttler:
    """Throttle function calls.

    A throttled function will execute at most once per specified time period.
    """

    def __init__(
        self,
        func: Callable[..., Any],
        wait: float = 0.2,
        leading: bool = False,
        trailing: bool = True,
    ):
        """Initialize throttler.

        Args:
            func: Function to throttle
            wait: Wait time in seconds, defaults to 0.2
            leading: Execute on leading edge, defaults to False
            trailing: Execute on trailing edge, defaults to True
        """
        self.func = func
        self.wait = wait
        self.leading = leading
        self.trailing = trailing
        self.timer: threading.Timer | None = None
        self.last_args: tuple[Any, ...] = ()
        self.last_kwargs: dict[str, Any] = {}
        self.result: Any = None
        self.is_leading_executed = False
        self.is_trailing_executed = False
        self.lock = threading.Lock()

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """Call the throttled function."""
        with self.lock:
            self.last_args = args
            self.last_kwargs = kwargs

            if self.timer is None:
                if self.leading and not self.is_leading_executed:
                    self.result = self.func(*args, **kwargs)
                    self.is_leading_executed = True

                if not self.leading and not self.trailing and self.is_trailing_executed:
                    self.result = self.func(*args, **kwargs)
                    self.is_trailing_executed = False

                self.timer = threading.Timer(self.wait, self._on_timeout)
                self.timer.start()

            return self.result

    def _on_timeout(self) -> None:
        """Handle timeout event."""
        with self.lock:
            if self.trailing:
                self.result = self.func(*self.last_args, **self.last_kwargs)

            self.timer = None
            self.is_leading_executed = False
            self.is_trailing_executed = True

    def cancel(self) -> None:
        """Cancel pending function call."""
        with self.lock:
            if self.timer:
                self.timer.cancel()
                self.timer = None
            self.is_leading_executed = False
            self.is_trailing_executed = False

    def flush(self) -> Any:
        """Immediately execute pending function call."""
        with self.lock:
            if self.timer is None:
                return self.result

            self.timer.cancel()
            self.timer = None
            self.is_leading_executed = False
            self.is_trailing_executed = False
            self.result = self.func(*self.last_args, **self.last_kwargs)
            return self.result


def throttle(
    wait: float = 0.2, leading: bool = False, trailing: bool = True
) -> Callable[[F], Throttler]:
    """Decorator to throttle function calls.

    Args:
        wait: Wait time in seconds, defaults to 0.2
        leading: Execute on leading edge, defaults to False
        trailing: Execute on trailing edge, defaults to True

    Returns:
        Throttled function

    Examples:
        >>> @throttle(wait=0.1)
        ... def api_call(data):
        ...     print(f"API call with {data}")
        >>>
        >>> api_call("test1")  # Executes immediately
        >>> api_call("test2")  # Ignored (within throttle period)
    """

    def decorator(func: F) -> Throttler:
        return Throttler(func, wait, leading, trailing)

    return decorator


class PollingController:
    """Controller for polling operations."""

    def __init__(
        self,
        task: Callable[[], Awaitable[T]],
        stop_condition: Callable[[T], bool] | None = None,
        error_action: Callable[[Exception], None] | None = None,
        on_progress: Callable[[T], None] | None = None,
        quit_on_error: bool = True,
        interval: float = 5.0,
        max_retries: int = 3,
        immediate: bool = False,
        max_executions: int | float = float("inf"),
    ):
        """Initialize polling controller.

        Args:
            task: Async task to poll
            stop_condition: Function to determine when to stop polling
            error_action: Function to handle errors
            on_progress: Function called on each successful execution
            quit_on_error: Whether to quit on max retries reached
            interval: Polling interval in seconds
            max_retries: Maximum retry attempts
            immediate: Whether to execute immediately
            max_executions: Maximum number of executions
        """
        self.task = task
        self.stop_condition = stop_condition or (lambda x: False)
        self.error_action = error_action
        self.on_progress = on_progress
        self.quit_on_error = quit_on_error
        self.interval = interval
        self.max_retries = max_retries
        self.immediate = immediate
        self.max_executions = max_executions

        self.is_active = False
        self.retry_count = 0
        self.execution_count = 0
        self.last_result: T | None = None
        self.last_error: Exception | None = None
        self._task: asyncio.Task[Any] | None = None

    async def start(self) -> None:
        """Start polling."""
        self.is_active = True

        if self.immediate:
            await self._execute_poll()
        else:
            await asyncio.sleep(self.interval)
            await self._execute_poll()

    def stop(self) -> None:
        """Stop polling."""
        self.is_active = False
        if self._task:
            self._task.cancel()

    async def _execute_poll(self) -> None:
        """Execute polling loop."""
        while self.is_active and self.execution_count < self.max_executions:
            try:
                result = await self.task()
                self.execution_count += 1
                self.last_result = result

                if self.on_progress:
                    self.on_progress(result)

                if self.stop_condition(result):
                    self.is_active = False
                    break

            except Exception as error:
                self.last_error = error
                self.retry_count += 1

                if self.error_action:
                    self.error_action(error)

                if self.quit_on_error and self.retry_count >= self.max_retries:
                    self.is_active = False
                    raise error

            if self.is_active and self.execution_count < self.max_executions:
                await asyncio.sleep(self.interval)

        # Set is_active to False when loop ends due to max_executions reached
        if self.execution_count >= self.max_executions:
            self.is_active = False

    def status(self) -> dict[str, Any]:
        """Get current status."""
        return {
            "status": "running" if self.is_active else "stopped",
            "retry_count": self.retry_count,
            "execution_count": self.execution_count,
            "last_result": self.last_result,
            "last_error": self.last_error,
        }


def create_polling(
    task: Callable[[], Awaitable[T]],
    stop_condition: Callable[[T], bool] | None = None,
    error_action: Callable[[Exception], None] | None = None,
    on_progress: Callable[[T], None] | None = None,
    quit_on_error: bool = True,
    interval: float = 5.0,
    max_retries: int = 3,
    immediate: bool = False,
    max_executions: int | float = float("inf"),
) -> PollingController:
    """Create a polling controller.

    Args:
        task: Async task to poll
        stop_condition: Function to determine when to stop polling
        error_action: Function to handle errors
        on_progress: Function called on each successful execution
        quit_on_error: Whether to quit on max retries reached
        interval: Polling interval in seconds
        max_retries: Maximum retry attempts
        immediate: Whether to execute immediately
        max_executions: Maximum number of executions

    Returns:
        Polling controller

    Examples:
        >>> async def fetch_data():
        ...     # Simulate API call
        ...     return {'status': 'processing'}
        >>>
        >>> poller = create_polling(
        ...     task=fetch_data,
        ...     stop_condition=lambda data: data['status'] == 'done',
        ...     interval=2.0
        ... )
        >>> # await poller.start()
    """
    return PollingController(
        task=task,
        stop_condition=stop_condition,
        error_action=error_action,
        on_progress=on_progress,
        quit_on_error=quit_on_error,
        interval=interval,
        max_retries=max_retries,
        immediate=immediate,
        max_executions=max_executions,
    )


def with_retry(
    max_retries: int = 3,
    delay: float = 0,
    should_retry: Callable[[Exception], bool] | None = None,
) -> Callable[[F], F]:
    """Decorator to add retry functionality to a function.

    Args:
        max_retries: Maximum number of retry attempts
        delay: Delay between retries in seconds
        should_retry: Function to determine if error should trigger retry

    Returns:
        Decorated function with retry capability

    Examples:
        >>> @with_retry(max_retries=3, delay=0.1)
        ... def unreliable_function():
        ...     import random
        ...     if random.random() < 0.7:
        ...         raise Exception("Random failure")
        ...     return "Success"
        >>>
        >>> # result = unreliable_function()  # Will retry up to 3 times
    """

    def decorator(func: F) -> F:
        if asyncio.iscoroutinefunction(func):

            @wraps(func)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                retry_count = 0
                last_error = None

                while retry_count <= max_retries:
                    try:
                        return await func(*args, **kwargs)
                    except Exception as error:
                        last_error = error
                        retry_count += 1

                        if retry_count > max_retries or (
                            should_retry and not should_retry(error)
                        ):
                            raise error

                        if delay > 0:
                            await asyncio.sleep(delay)

                if last_error:
                    raise last_error

            return async_wrapper  # type: ignore
        else:

            @wraps(func)
            def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
                retry_count = 0
                last_error = None

                while retry_count <= max_retries:
                    try:
                        return func(*args, **kwargs)
                    except Exception as error:
                        last_error = error
                        retry_count += 1

                        if retry_count > max_retries or (
                            should_retry and not should_retry(error)
                        ):
                            raise error

                        if delay > 0:
                            time.sleep(delay)

                if last_error:
                    raise last_error

            return sync_wrapper  # type: ignore

    return decorator


def memoize(func: F) -> F:
    """Decorator to memoize function results.

    Args:
        func: Function to memoize

    Returns:
        Memoized function

    Examples:
        >>> @memoize
        ... def expensive_calculation(n):
        ...     print(f"Computing for {n}")
        ...     return n * n
        >>>
        >>> expensive_calculation(5)  # Prints "Computing for 5"
        25
        >>> expensive_calculation(5)  # Uses cached result, no print
        25
    """
    cache: dict[tuple[Any, ...], Any] = {}

    if asyncio.iscoroutinefunction(func):

        @wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            # Create cache key from args and kwargs
            key = (args, tuple(sorted(kwargs.items())))

            if key not in cache:
                cache[key] = await func(*args, **kwargs)

            return cache[key]

        async_wrapper.cache = cache  # type: ignore
        async_wrapper.cache_clear = lambda: cache.clear()  # type: ignore

        return async_wrapper  # type: ignore
    else:

        @wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            # Create cache key from args and kwargs
            key = (args, tuple(sorted(kwargs.items())))

            if key not in cache:
                cache[key] = func(*args, **kwargs)

            return cache[key]

        sync_wrapper.cache = cache  # type: ignore
        sync_wrapper.cache_clear = lambda: cache.clear()  # type: ignore

        return sync_wrapper  # type: ignore


def once(func: F) -> F:
    """Decorator to ensure function is called only once.

    Args:
        func: Function to call once

    Returns:
        Function that can only be called once

    Examples:
        >>> @once
        ... def initialize():
        ...     print("Initializing...")
        ...     return "initialized"
        >>>
        >>> initialize()  # Prints "Initializing..."
        'initialized'
        >>> initialize()  # Returns cached result, no print
        'initialized'
    """
    called = False
    result = None

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        nonlocal called, result
        if not called:
            result = func(*args, **kwargs)
            called = True
        return result

    return wrapper  # type: ignore
