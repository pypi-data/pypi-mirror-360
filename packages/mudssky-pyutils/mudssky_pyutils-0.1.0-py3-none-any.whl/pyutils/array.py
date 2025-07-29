"""Array utility functions.

This module provides utility functions for working with arrays/lists,
ported from the jsutils library.
"""

import random
from collections.abc import Callable, Generator
from typing import (
    Any,
    TypeVar,
)


T = TypeVar("T")
K = TypeVar("K")
V = TypeVar("V")


def range_list(start: int, end: int | None = None, step: int = 1) -> list[int]:
    """Generate a list of integers from start to end (exclusive).

    Args:
        start: Starting value (or end if end is None)
        end: Ending value (exclusive), optional
        step: Step size, defaults to 1

    Returns:
        List of integers

    Examples:
        >>> range_list(5)
        [0, 1, 2, 3, 4]
        >>> range_list(2, 5)
        [2, 3, 4]
        >>> range_list(0, 10, 2)
        [0, 2, 4, 6, 8]
    """
    if end is None:
        end = start
        start = 0
    return list(range(start, end, step))


def range_iter(
    start: int, end: int | None = None, step: int = 1
) -> Generator[int, None, None]:
    """Generate integers from start to end (exclusive).

    Args:
        start: Starting value (or end if end is None)
        end: Ending value (exclusive), optional
        step: Step size, defaults to 1

    Yields:
        Integer values

    Examples:
        >>> list(range_iter(3))
        [0, 1, 2]
        >>> list(range_iter(1, 4))
        [1, 2, 3]
    """
    if end is None:
        end = start
        start = 0
    yield from range(start, end, step)


def boil(
    items: list[T], reducer_fn: Callable[[T, T], T], initial_value: T | None = None
) -> T | None:
    """Reduce a list to a single value using a reducer function.

    Args:
        items: List of items to reduce
        reducer_fn: Function that takes accumulator and current item,
            returns new accumulator
        initial_value: Initial value for the accumulator

    Returns:
        The final reduced value, or initial_value if list is empty

    Examples:
        >>> boil([1, 2, 3, 4], lambda acc, x: acc + x, 0)
        10
        >>> boil([1, 2, 3, 4], lambda acc, x: acc * x, 1)
        24
        >>> boil(['a', 'b', 'c'], lambda acc, x: acc + x, '')
        'abc'
    """
    if not items:
        return initial_value

    if initial_value is None:
        result = items[0]
        start_index = 1
    else:
        result = initial_value
        start_index = 0

    for item in items[start_index:]:
        result = reducer_fn(result, item)
    return result


def chunk(items: list[T], size: int) -> list[list[T]]:
    """Split a list into chunks of specified size.

    Args:
        items: List to split
        size: Size of each chunk

    Returns:
        List of chunks

    Raises:
        ValueError: If size is less than or equal to 0

    Examples:
        >>> chunk([1, 2, 3, 4, 5], 2)
        [[1, 2], [3, 4], [5]]
        >>> chunk(['a', 'b', 'c', 'd'], 3)
        [['a', 'b', 'c'], ['d']]
    """
    if size <= 0:
        raise ValueError("Chunk size must be greater than 0")
    return [items[i : i + size] for i in range(0, len(items), size)]


def count_by(items: list[T], key_fn: Callable[[T], K]) -> dict[K, int]:
    """Count items by a key function.

    Args:
        items: List of items to count
        key_fn: Function to extract key from each item

    Returns:
        Dictionary mapping keys to counts

    Examples:
        >>> count_by(['apple', 'banana', 'apricot'], lambda x: x[0])
        {'a': 2, 'b': 1}
        >>> count_by([1, 2, 3, 4, 5], lambda x: x % 2)
        {1: 3, 0: 2}
    """
    result: dict[K, int] = {}
    for item in items:
        key = key_fn(item)
        result[key] = result.get(key, 0) + 1
    return result


def diff(old_list: list[T], new_list: list[T]) -> list[T]:
    """Find items that are in old_list but not in new_list.

    Args:
        old_list: Original list
        new_list: New list

    Returns:
        List of items that were removed (in old_list but not in new_list)

    Examples:
        >>> diff([1, 2, 3, 4], [2, 4])
        [1, 3]
        >>> diff([1, 2, 3], [1, 2, 3])
        []
        >>> diff([1, 1, 2, 3], [1])
        [2, 3]
    """
    new_set = set(new_list)
    return [item for item in old_list if item not in new_set]


def first(items: list[T], default: T | None = None) -> T | None:
    """Get the first item from a list.

    Args:
        items: List to get first item from
        default: Default value if list is empty

    Returns:
        First item or default value

    Examples:
        >>> first([1, 2, 3])
        1
        >>> first([], 'default')
        'default'
    """
    return items[0] if items else default


def last(items: list[T], default: T | None = None) -> T | None:
    """Get the last item from a list.

    Args:
        items: List to get last item from
        default: Default value if list is empty

    Returns:
        Last item or default value

    Examples:
        >>> last([1, 2, 3])
        3
        >>> last([], 'default')
        'default'
    """
    return items[-1] if items else default


def fork(items: list[T], condition: Callable[[T], bool]) -> tuple[list[T], list[T]]:
    """Split a list into two based on a condition.

    Args:
        items: List to split
        condition: Function to test each item

    Returns:
        Tuple of (items_matching_condition, items_not_matching_condition)

    Examples:
        >>> fork([1, 2, 3, 4, 5], lambda x: x % 2 == 0)
        ([2, 4], [1, 3, 5])
        >>> fork(['apple', 'banana', 'cherry'], lambda x: len(x) > 5)
        (['banana', 'cherry'], ['apple'])
    """
    true_items = []
    false_items = []

    for item in items:
        if condition(item):
            true_items.append(item)
        else:
            false_items.append(item)

    return true_items, false_items


def has_intersects(list1: list[T], list2: list[T]) -> bool:
    """Check if two lists have any common elements.

    Args:
        list1: First list
        list2: Second list

    Returns:
        True if lists have common elements, False otherwise

    Examples:
        >>> has_intersects([1, 2, 3], [3, 4, 5])
        True
        >>> has_intersects([1, 2], [3, 4])
        False
    """
    set1 = set(list1)
    return any(item in set1 for item in list2)


def max_by(items: list[T], key_fn: Callable[[T], Any]) -> T | None:
    """Find the item with the maximum value according to a key function.

    Args:
        items: List of items
        key_fn: Function to extract comparison value

    Returns:
        Item with maximum value, or None if list is empty

    Examples:
        >>> max_by(['apple', 'banana', 'cherry'], len)
        'banana'
        >>> max_by([{'age': 20}, {'age': 30}, {'age': 25}], lambda x: x['age'])
        {'age': 30}
    """
    if not items:
        return None
    return max(items, key=key_fn)


def min_by(items: list[T], key_fn: Callable[[T], Any]) -> T | None:
    """Find the item with the minimum value according to a key function.

    Args:
        items: List of items
        key_fn: Function to extract comparison value

    Returns:
        Item with minimum value, or None if list is empty

    Examples:
        >>> min_by(['apple', 'banana', 'cherry'], len)
        'apple'
        >>> min_by([{'age': 20}, {'age': 30}, {'age': 25}], lambda x: x['age'])
        {'age': 20}
    """
    if not items:
        return None
    return min(items, key=key_fn)


def toggle(items: list[T], item: T) -> list[T]:
    """Add item to list if not present, remove if present.

    Args:
        items: List to toggle item in
        item: Item to toggle

    Returns:
        New list with item toggled

    Examples:
        >>> toggle([1, 2, 3], 4)
        [1, 2, 3, 4]
        >>> toggle([1, 2, 3], 2)
        [1, 3]
    """
    result = items.copy()
    if item in result:
        result.remove(item)
    else:
        result.append(item)
    return result


def sum_by(items: list[T], key_fn: Callable[[T], int | float]) -> int | float:
    """Sum values extracted from items using a key function.

    Args:
        items: List of items
        key_fn: Function to extract numeric value from each item

    Returns:
        Sum of extracted values

    Examples:
        >>> sum_by([{'value': 10}, {'value': 20}, {'value': 30}], lambda x: x['value'])
        60
        >>> sum_by(['hello', 'world', 'python'], len)
        16
    """
    return sum(key_fn(item) for item in items)


def zip_object(keys: list[K], values: list[V]) -> dict[K, V]:
    """Create a dictionary from lists of keys and values.

    Args:
        keys: List of keys
        values: List of values

    Returns:
        Dictionary mapping keys to values

    Examples:
        >>> zip_object(['a', 'b', 'c'], [1, 2, 3])
        {'a': 1, 'b': 2, 'c': 3}
        >>> zip_object(['name', 'age'], ['Alice', 25])
        {'name': 'Alice', 'age': 25}
    """
    return dict(zip(keys, values, strict=False))


def zip_lists(*lists: list[T]) -> list[tuple[T, ...]]:
    """Zip multiple lists together.

    Args:
        *lists: Variable number of lists to zip

    Returns:
        List of tuples containing corresponding elements

    Examples:
        >>> zip_lists([1, 2, 3], ['a', 'b', 'c'])
        [(1, 'a'), (2, 'b'), (3, 'c')]
        >>> zip_lists([1, 2], [3, 4], [5, 6])
        [(1, 3, 5), (2, 4, 6)]
    """
    return list(zip(*lists, strict=False))


def unique(items: list[T]) -> list[T]:
    """Remove duplicate items from a list while preserving order.

    Args:
        items: List with potential duplicates

    Returns:
        List with duplicates removed

    Examples:
        >>> unique([1, 2, 2, 3, 1, 4])
        [1, 2, 3, 4]
        >>> unique(['a', 'b', 'a', 'c', 'b'])
        ['a', 'b', 'c']
    """
    seen = set()
    result = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


def shuffle(items: list[T]) -> list[T]:
    """Return a new list with items in random order.

    Args:
        items: List to shuffle

    Returns:
        New shuffled list

    Examples:
        >>> original = [1, 2, 3, 4, 5]
        >>> shuffled = shuffle(original)
        >>> len(shuffled) == len(original)
        True
        >>> set(shuffled) == set(original)
        True
    """
    result = items.copy()
    random.shuffle(result)
    return result


def alphabetical(
    items: list[str], key_fn: Callable[[str], str] | None = None
) -> list[str]:
    """Sort strings alphabetically (case-insensitive by default).

    Args:
        items: List of strings to sort
        key_fn: Optional function to extract sort key from each string

    Returns:
        New sorted list

    Examples:
        >>> alphabetical(['banana', 'apple', 'cherry'])
        ['apple', 'banana', 'cherry']
        >>> alphabetical(['Banana', 'apple', 'Cherry'])
        ['apple', 'Banana', 'Cherry']
    """
    if key_fn is None:
        # Default to case-insensitive sorting while preserving original case
        return sorted(items, key=str.lower)
    return sorted(items, key=key_fn)


def filter_list(items: list[T], predicate: Callable[[T], bool]) -> list[T]:
    """Filter a list based on a predicate function.

    Args:
        items: List to filter
        predicate: Function that returns True for items to keep

    Returns:
        New list containing only items that match the predicate

    Examples:
        >>> filter_list([1, 2, 3, 4, 5], lambda x: x % 2 == 0)
        [2, 4]
        >>> filter_list(['apple', 'banana', 'cherry'], lambda x: len(x) > 5)
        ['banana', 'cherry']
        >>> filter_list(
        ...     ['DB_HOST=localhost', 'DB_PORT=5432', 'API_KEY=secret'],
        ...     lambda x: x.startswith('DB_')
        ... )
        ['DB_HOST=localhost', 'DB_PORT=5432']
    """
    return [item for item in items if predicate(item)]
