"""Collection utility functions.

This module provides utility functions for working with collections,
inspired by JavaScript array and object methods that are commonly used
but not directly available in Python.
"""

from collections.abc import Callable
from typing import Any, TypeVar


T = TypeVar("T")
K = TypeVar("K")
V = TypeVar("V")


def flat_map(items: list[T], mapper: Callable[[T], list[Any]]) -> list[Any]:
    """Map each element and flatten the result.

    Similar to JavaScript's Array.prototype.flatMap().

    Args:
        items: List of items to map and flatten
        mapper: Function that maps each item to a list

    Returns:
        Flattened list of mapped results

    Examples:
        >>> flat_map([1, 2, 3], lambda x: [x, x * 2])
        [1, 2, 2, 4, 3, 6]
        >>> flat_map(['hello', 'world'], lambda x: list(x))
        ['h', 'e', 'l', 'l', 'o', 'w', 'o', 'r', 'l', 'd']
    """
    result = []
    for item in items:
        mapped = mapper(item)
        if isinstance(mapped, list):
            result.extend(mapped)
        else:
            result.append(mapped)  # type: ignore[unreachable]
    return result


def includes(items: list[T], search_item: T, from_index: int = 0) -> bool:
    """Check if an array includes a certain value.

    Similar to JavaScript's Array.prototype.includes().

    Args:
        items: List to search in
        search_item: Item to search for
        from_index: Index to start searching from

    Returns:
        True if item is found, False otherwise

    Examples:
        >>> includes([1, 2, 3], 2)
        True
        >>> includes([1, 2, 3], 4)
        False
        >>> includes([1, 2, 3, 2], 2, 2)
        True
    """
    try:
        return search_item in items[from_index:]
    except (IndexError, TypeError):
        return False


def find_index(
    items: list[T], predicate: Callable[[T], bool], from_index: int = 0
) -> int:
    """Find the index of the first element that satisfies the predicate.

    Similar to JavaScript's Array.prototype.findIndex().

    Args:
        items: List to search in
        predicate: Function to test each element
        from_index: Index to start searching from

    Returns:
        Index of first matching element, or -1 if not found

    Examples:
        >>> find_index([1, 2, 3, 4], lambda x: x > 2)
        2
        >>> find_index([1, 2, 3, 4], lambda x: x > 10)
        -1
    """
    for i, item in enumerate(items[from_index:], from_index):
        if predicate(item):
            return i
    return -1


def find_last_index(items: list[T], predicate: Callable[[T], bool]) -> int:
    """Find the index of the last element that satisfies the predicate.

    Similar to JavaScript's Array.prototype.findLastIndex().

    Args:
        items: List to search in
        predicate: Function to test each element

    Returns:
        Index of last matching element, or -1 if not found

    Examples:
        >>> find_last_index([1, 2, 3, 2, 4], lambda x: x == 2)
        3
        >>> find_last_index([1, 2, 3, 4], lambda x: x > 10)
        -1
    """
    for i in range(len(items) - 1, -1, -1):
        if predicate(items[i]):
            return i
    return -1


def some(items: list[T], predicate: Callable[[T], bool]) -> bool:
    """Test whether at least one element passes the test.

    Similar to JavaScript's Array.prototype.some().

    Args:
        items: List to test
        predicate: Function to test each element

    Returns:
        True if at least one element passes the test

    Examples:
        >>> some([1, 2, 3, 4], lambda x: x > 3)
        True
        >>> some([1, 2, 3, 4], lambda x: x > 10)
        False
    """
    return any(predicate(item) for item in items)


def every(items: list[T], predicate: Callable[[T], bool]) -> bool:
    """Test whether all elements pass the test.

    Similar to JavaScript's Array.prototype.every().

    Args:
        items: List to test
        predicate: Function to test each element

    Returns:
        True if all elements pass the test

    Examples:
        >>> every([2, 4, 6, 8], lambda x: x % 2 == 0)
        True
        >>> every([1, 2, 3, 4], lambda x: x % 2 == 0)
        False
    """
    return all(predicate(item) for item in items)


def at(items: list[T], index: int) -> T | None:
    """Get element at the given index, supporting negative indices.

    Similar to JavaScript's Array.prototype.at().

    Args:
        items: List to access
        index: Index to access (can be negative)

    Returns:
        Element at the index, or None if index is out of bounds

    Examples:
        >>> at([1, 2, 3, 4], 1)
        2
        >>> at([1, 2, 3, 4], -1)
        4
        >>> at([1, 2, 3, 4], 10)
    """
    try:
        return items[index]
    except IndexError:
        return None


def fill(items: list[T], value: Any, start: int = 0, end: int | None = None) -> list[T]:
    """Fill array elements with a static value.

    Similar to JavaScript's Array.prototype.fill().

    Args:
        items: List to fill (modified in place)
        value: Value to fill with
        start: Start index
        end: End index (exclusive)

    Returns:
        The modified list

    Examples:
        >>> fill([1, 2, 3, 4], 0)
        [0, 0, 0, 0]
        >>> fill([1, 2, 3, 4], 0, 1, 3)
        [1, 0, 0, 4]
    """
    if end is None:
        end = len(items)

    for i in range(start, min(end, len(items))):
        items[i] = value

    return items


def copy_within(
    items: list[T], target: int, start: int = 0, end: int | None = None
) -> list[T]:
    """Copy array elements within the array to another position.

    Similar to JavaScript's Array.prototype.copyWithin().

    Args:
        items: List to modify (modified in place)
        target: Index to copy elements to
        start: Index to start copying from
        end: Index to stop copying from (exclusive)

    Returns:
        The modified list

    Examples:
        >>> copy_within([1, 2, 3, 4, 5], 0, 3)
        [4, 5, 3, 4, 5]
        >>> copy_within([1, 2, 3, 4, 5], 2, 0, 2)
        [1, 2, 1, 2, 5]
    """
    if end is None:
        end = len(items)

    # Create a copy of the slice to avoid issues with overlapping ranges
    slice_to_copy = items[start:end]

    # Copy elements to target position
    for i, value in enumerate(slice_to_copy):
        if target + i < len(items):
            items[target + i] = value

    return items


def group_by(items: list[T], key_fn: Callable[[T], K]) -> dict[K, list[T]]:
    """Group array elements by a key function.

    Similar to JavaScript's Object.groupBy() (proposed).

    Args:
        items: List of items to group
        key_fn: Function to extract grouping key

    Returns:
        Dictionary mapping keys to lists of items

    Examples:
        >>> group_by(['apple', 'banana', 'apricot'], lambda x: x[0])
        {'a': ['apple', 'apricot'], 'b': ['banana']}
        >>> group_by([1, 2, 3, 4, 5], lambda x: x % 2)
        {1: [1, 3, 5], 0: [2, 4]}
    """
    result: dict[K, list[T]] = {}
    for item in items:
        key = key_fn(item)
        if key not in result:
            result[key] = []
        result[key].append(item)
    return result


def to_reversed(items: list[T]) -> list[T]:
    """Return a new array with elements in reversed order.

    Similar to JavaScript's Array.prototype.toReversed().

    Args:
        items: List to reverse

    Returns:
        New list with elements in reversed order

    Examples:
        >>> to_reversed([1, 2, 3, 4])
        [4, 3, 2, 1]
        >>> original = [1, 2, 3]
        >>> reversed_list = to_reversed(original)
        >>> original
        [1, 2, 3]
    """
    return items[::-1]


def to_sorted(
    items: list[T], key: Callable[[T], Any] | None = None, reverse: bool = False
) -> list[T]:
    """Return a new sorted array.

    Similar to JavaScript's Array.prototype.toSorted().

    Args:
        items: List to sort
        key: Function to extract comparison key
        reverse: Whether to sort in reverse order

    Returns:
        New sorted list

    Examples:
        >>> to_sorted([3, 1, 4, 1, 5])
        [1, 1, 3, 4, 5]
        >>> to_sorted(['banana', 'apple', 'cherry'], key=len)
        ['apple', 'banana', 'cherry']
    """
    return sorted(items, key=key, reverse=reverse)  # type: ignore[type-var,arg-type]


def with_item(items: list[T], index: int, value: T) -> list[T]:
    """Return a new array with one element changed.

    Similar to JavaScript's Array.prototype.with().

    Args:
        items: Original list
        index: Index to change
        value: New value

    Returns:
        New list with the element changed

    Examples:
        >>> with_item([1, 2, 3, 4], 1, 'two')
        [1, 'two', 3, 4]
        >>> original = [1, 2, 3]
        >>> modified = with_item(original, 0, 'one')
        >>> original
        [1, 2, 3]
    """
    result = items.copy()
    if 0 <= index < len(result):
        result[index] = value
    elif -len(result) <= index < 0:
        result[index] = value
    return result


def entries(items: list[T]) -> list[tuple[int, T]]:
    """Return array of [index, value] pairs.

    Similar to JavaScript's Array.prototype.entries().

    Args:
        items: List to get entries from

    Returns:
        List of (index, value) tuples

    Examples:
        >>> entries(['a', 'b', 'c'])
        [(0, 'a'), (1, 'b'), (2, 'c')]
    """
    return list(enumerate(items))


def keys(items: list[T]) -> list[int]:
    """Return array of indices.

    Similar to JavaScript's Array.prototype.keys().

    Args:
        items: List to get keys from

    Returns:
        List of indices

    Examples:
        >>> keys(['a', 'b', 'c'])
        [0, 1, 2]
    """
    return list(range(len(items)))


def values(items: list[T]) -> list[T]:
    """Return array of values (copy of the array).

    Similar to JavaScript's Array.prototype.values().

    Args:
        items: List to get values from

    Returns:
        Copy of the list

    Examples:
        >>> values(['a', 'b', 'c'])
        ['a', 'b', 'c']
    """
    return items.copy()


def splice(
    items: list[T], start: int, delete_count: int = 0, *insert_items: T
) -> list[T]:
    """Change array contents by removing/replacing existing elements.

    Also supports adding new elements.

    Similar to JavaScript's Array.prototype.splice().

    Args:
        items: List to modify (modified in place)
        start: Index to start changing the array
        delete_count: Number of elements to remove
        *insert_items: Items to insert

    Returns:
        List of removed elements

    Examples:
        >>> arr = [1, 2, 3, 4, 5]
        >>> removed = splice(arr, 2, 1, 'a', 'b')
        >>> arr
        [1, 2, 'a', 'b', 4, 5]
        >>> removed
        [3]
    """
    # Handle negative start index
    if start < 0:
        start = max(0, len(items) + start)
    else:
        start = min(start, len(items))

    # Handle delete_count
    delete_count = max(0, min(delete_count, len(items) - start))

    # Remove elements and get removed items
    removed = items[start : start + delete_count]

    # Replace with new items
    items[start : start + delete_count] = insert_items

    return removed
