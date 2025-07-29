"""Async utility functions.

This module provides utility functions for working with asynchronous operations,
including sleep, timeout, and concurrent execution utilities,
ported from the jsutils library.
"""

import asyncio
import time
from collections.abc import Awaitable, Callable
from typing import Any, TypeVar


T = TypeVar("T")


async def sleep_async(seconds: float) -> None:
    """Asynchronously sleep for the specified number of seconds.

    Args:
        seconds: Number of seconds to sleep

    Examples:
        >>> import asyncio
        >>> async def main():
        ...     await sleep_async(0.1)
        ...     print("Slept for 0.1 seconds")
        >>> # asyncio.run(main())
    """
    await asyncio.sleep(seconds)


async def timeout(
    coro: Awaitable[T], timeout_seconds: float, default: T | None = None
) -> T:
    """Execute coroutine with timeout.

    Args:
        coro: Coroutine to execute
        timeout_seconds: Timeout in seconds
        default: Default value to return on timeout

    Returns:
        Result of coroutine or default value

    Raises:
        asyncio.TimeoutError: If timeout occurs and no default provided

    Examples:
        >>> async def slow_operation():
        ...     await asyncio.sleep(2)
        ...     return "done"
        >>>
        >>> async def main():
        ...     result = await timeout(slow_operation(), 1.0, "timeout")
        ...     print(result)  # "timeout"
        >>> # asyncio.run(main())
    """
    try:
        return await asyncio.wait_for(coro, timeout=timeout_seconds)
    except asyncio.TimeoutError:
        if default is not None:
            return default
        raise


async def delay(value: T, seconds: float) -> T:
    """Return a value after a delay.

    Args:
        value: Value to return after delay
        seconds: Delay in seconds

    Returns:
        The provided value after delay

    Examples:
        >>> async def main():
        ...     result = await delay("hello", 0.1)
        ...     print(result)  # "hello" (after 0.1 seconds)
        >>> # asyncio.run(main())
    """
    await asyncio.sleep(seconds)
    return value


async def gather_with_concurrency(
    *coroutines: Awaitable[T], limit: int = 10
) -> list[T]:
    """Execute coroutines with concurrency limit.

    Args:
        *coroutines: Coroutines to execute
        limit: Maximum number of concurrent executions

    Returns:
        List of results in order

    Examples:
        >>> async def fetch_data(i):
        ...     await asyncio.sleep(0.1)
        ...     return f"data_{i}"
        >>>
        >>> async def main():
        ...     tasks = [fetch_data(i) for i in range(5)]
        ...     results = await gather_with_concurrency(*tasks, limit=2)
        ...     print(results)  # ['data_0', 'data_1', 'data_2', 'data_3', 'data_4']
        >>> # asyncio.run(main())
    """
    semaphore = asyncio.Semaphore(limit)

    async def limited_coro(coro: Awaitable[T]) -> T:
        async with semaphore:
            return await coro

    return await asyncio.gather(*[limited_coro(coro) for coro in coroutines])


async def race(*coroutines: Awaitable[T]) -> T:
    """Return the result of the first coroutine to complete.

    Args:
        *coroutines: Coroutines to race

    Returns:
        Result of the first completed coroutine

    Examples:
        >>> async def slow():
        ...     await asyncio.sleep(1)
        ...     return "slow"
        >>>
        >>> async def fast():
        ...     await asyncio.sleep(0.1)
        ...     return "fast"
        >>>
        >>> async def main():
        ...     result = await race(slow(), fast())
        ...     print(result)  # "fast"
        >>> # asyncio.run(main())
    """
    # Convert coroutines to tasks explicitly
    tasks: list[asyncio.Task[T]] = []
    for coro in coroutines:
        if asyncio.iscoroutine(coro):
            tasks.append(asyncio.create_task(coro))
        else:
            # Convert awaitable to coroutine
            async def _wrap(c: Awaitable[T] = coro) -> T:
                return await c

            tasks.append(asyncio.create_task(_wrap()))

    done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)

    # Cancel pending tasks
    for task in pending:
        task.cancel()

    # Return result of first completed task
    completed_task = done.pop()
    return completed_task.result()


async def retry_async(
    coro_func: Callable[[], Awaitable[T]],
    max_retries: int = 3,
    delay: float = 0,
    backoff_factor: float = 1,
    should_retry: Callable[[Exception], bool] | None = None,
) -> T:
    """Retry an async function with exponential backoff.

    Args:
        coro_func: Function that returns a coroutine
        max_retries: Maximum number of retry attempts
        delay: Initial delay between retries in seconds
        backoff_factor: Multiplier for delay on each retry
        should_retry: Function to determine if error should trigger retry

    Returns:
        Result of successful execution

    Raises:
        Exception: Last exception if all retries failed

    Examples:
        >>> async def unreliable_api():
        ...     import random
        ...     if random.random() < 0.7:
        ...         raise Exception("API Error")
        ...     return "success"
        >>>
        >>> async def main():
        ...     result = await retry_async(
        ...         unreliable_api,
        ...         max_retries=3,
        ...         delay=0.1,
        ...         backoff_factor=2
        ...     )
        ...     print(result)
        >>> # asyncio.run(main())
    """
    last_error = None
    current_delay = delay

    for attempt in range(max_retries + 1):
        try:
            return await coro_func()
        except Exception as error:
            last_error = error

            if attempt == max_retries or (should_retry and not should_retry(error)):
                break

            if current_delay > 0:
                await asyncio.sleep(current_delay)
                current_delay *= backoff_factor

    if last_error:
        raise last_error
    raise RuntimeError("No attempts were made")


async def map_async(
    func: Callable[[T], Awaitable[Any]], items: list[T], concurrency: int = 10
) -> list[Any]:
    """Apply async function to list of items with concurrency control.

    Args:
        func: Async function to apply
        items: List of items to process
        concurrency: Maximum concurrent executions

    Returns:
        List of results in order

    Examples:
        >>> async def process_item(item):
        ...     await asyncio.sleep(0.1)
        ...     return item * 2
        >>>
        >>> async def main():
        ...     items = [1, 2, 3, 4, 5]
        ...     results = await map_async(process_item, items, concurrency=2)
        ...     print(results)  # [2, 4, 6, 8, 10]
        >>> # asyncio.run(main())
    """
    semaphore = asyncio.Semaphore(concurrency)

    async def limited_func(item: T) -> Any:
        async with semaphore:
            return await func(item)

    return await asyncio.gather(*[limited_func(item) for item in items])


async def filter_async(
    predicate: Callable[[T], Awaitable[bool]], items: list[T], concurrency: int = 10
) -> list[T]:
    """Filter list using async predicate with concurrency control.

    Args:
        predicate: Async predicate function
        items: List of items to filter
        concurrency: Maximum concurrent executions

    Returns:
        Filtered list of items

    Examples:
        >>> async def is_even_async(n):
        ...     await asyncio.sleep(0.01)
        ...     return n % 2 == 0
        >>>
        >>> async def main():
        ...     numbers = [1, 2, 3, 4, 5, 6]
        ...     evens = await filter_async(is_even_async, numbers)
        ...     print(evens)  # [2, 4, 6]
        >>> # asyncio.run(main())
    """
    semaphore = asyncio.Semaphore(concurrency)

    async def check_item(item: T) -> tuple[T, bool]:
        async with semaphore:
            result = await predicate(item)
            return item, result

    results = await asyncio.gather(*[check_item(item) for item in items])
    return [item for item, passed in results if passed]


def run_in_thread(func: Callable[..., T], *args: Any, **kwargs: Any) -> Awaitable[T]:
    """Run a synchronous function in a thread pool.

    Args:
        func: Synchronous function to run
        *args: Positional arguments
        **kwargs: Keyword arguments

    Returns:
        Awaitable result

    Examples:
        >>> def cpu_intensive_task(n):
        ...     return sum(i * i for i in range(n))
        >>>
        >>> async def main():
        ...     result = await run_in_thread(cpu_intensive_task, 1000)
        ...     print(result)
        >>> # asyncio.run(main())
    """
    loop = asyncio.get_event_loop()
    return loop.run_in_executor(None, lambda: func(*args, **kwargs))


async def batch_process(
    items: list[T],
    processor: Callable[[list[T]], Awaitable[list[Any]]],
    batch_size: int = 100,
    concurrency: int = 5,
) -> list[Any]:
    """Process items in batches with concurrency control.

    Args:
        items: Items to process
        processor: Function to process a batch of items
        batch_size: Size of each batch
        concurrency: Maximum concurrent batch processing

    Returns:
        Flattened list of all results

    Examples:
        >>> async def process_batch(batch):
        ...     await asyncio.sleep(0.1)
        ...     return [item * 2 for item in batch]
        >>>
        >>> async def main():
        ...     items = list(range(10))
        ...     results = await batch_process(
        ...         items, process_batch, batch_size=3, concurrency=2
        ...     )
        ...     print(results)  # [0, 2, 4, 6, 8, 10, 12, 14, 16, 18]
        >>> # asyncio.run(main())
    """
    # Create batches
    batches = [items[i : i + batch_size] for i in range(0, len(items), batch_size)]

    # Process batches with concurrency control
    batch_results = await gather_with_concurrency(
        *[processor(batch) for batch in batches], limit=concurrency
    )

    # Flatten results
    result = []
    for batch_result in batch_results:
        result.extend(batch_result)

    return result


class AsyncContextManager:
    """Base class for async context managers."""

    async def __aenter__(self) -> "AsyncContextManager":
        """Enter async context."""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit async context."""
        pass


class AsyncTimer(AsyncContextManager):
    """Async context manager for timing operations."""

    def __init__(self) -> None:
        """Initialize timer."""
        self.start_time: float | None = None
        self.end_time: float | None = None
        self.elapsed: float | None = None

    async def __aenter__(self) -> "AsyncTimer":
        """Start timing."""
        self.start_time = time.time()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Stop timing."""
        self.end_time = time.time()
        if self.start_time is not None:
            self.elapsed = self.end_time - self.start_time


async def with_timeout_default(
    coro: Awaitable[T], timeout_seconds: float, default: T
) -> T:
    """Execute coroutine with timeout, returning default on timeout.

    Args:
        coro: Coroutine to execute
        timeout_seconds: Timeout in seconds
        default: Default value to return on timeout

    Returns:
        Result of coroutine or default value

    Examples:
        >>> async def slow_task():
        ...     await asyncio.sleep(2)
        ...     return "completed"
        >>>
        >>> async def main():
        ...     result = await with_timeout_default(
        ...         slow_task(), 1.0, "timed_out"
        ...     )
        ...     print(result)  # "timed_out"
        >>> # asyncio.run(main())
    """
    try:
        return await asyncio.wait_for(coro, timeout=timeout_seconds)
    except asyncio.TimeoutError:
        return default


async def wait_for_all(
    *coroutines: Awaitable[Any], timeout: float | None = None
) -> list[Any]:
    """Wait for all coroutines to complete.

    Args:
        *coroutines: Coroutines to wait for
        timeout: Optional timeout in seconds

    Returns:
        List of results

    Raises:
        asyncio.TimeoutError: If timeout occurs

    Examples:
        >>> async def task1():
        ...     await asyncio.sleep(0.1)
        ...     return "task1"
        >>>
        >>> async def task2():
        ...     await asyncio.sleep(0.2)
        ...     return "task2"
        >>>
        >>> async def main():
        ...     results = await wait_for_all(task1(), task2())
        ...     print(results)  # ["task1", "task2"]
        >>> # asyncio.run(main())
    """
    if timeout is None:
        return await asyncio.gather(*coroutines)
    else:
        return await asyncio.wait_for(asyncio.gather(*coroutines), timeout=timeout)


async def wait_for_any(*coroutines: Awaitable[T], timeout: float | None = None) -> T:
    """Wait for any coroutine to complete.

    Args:
        *coroutines: Coroutines to wait for
        timeout: Optional timeout in seconds

    Returns:
        Result of first completed coroutine

    Raises:
        asyncio.TimeoutError: If timeout occurs

    Examples:
        >>> async def slow_task():
        ...     await asyncio.sleep(1)
        ...     return "slow"
        >>>
        >>> async def fast_task():
        ...     await asyncio.sleep(0.1)
        ...     return "fast"
        >>>
        >>> async def main():
        ...     result = await wait_for_any(slow_task(), fast_task())
        ...     print(result)  # "fast"
        >>> # asyncio.run(main())
    """
    if timeout is None:
        return await race(*coroutines)
    else:
        return await asyncio.wait_for(race(*coroutines), timeout=timeout)
