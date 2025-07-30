"""Tests for collection utility functions."""

from pyutils.collection import (
    at,
    copy_within,
    entries,
    every,
    fill,
    find_index,
    find_last_index,
    flat_map,
    group_by,
    includes,
    keys,
    some,
    splice,
    to_reversed,
    to_sorted,
    values,
    with_item,
)


class TestFlatMap:
    """Tests for flat_map function."""

    def test_basic_flat_map(self):
        """Test basic flat_map functionality."""
        result = flat_map([1, 2, 3], lambda x: [x, x * 2])
        assert result == [1, 2, 2, 4, 3, 6]

    def test_flat_map_strings(self):
        """Test flat_map with strings."""
        result = flat_map(["hello", "world"], lambda x: list(x))
        assert result == ["h", "e", "l", "l", "o", "w", "o", "r", "l", "d"]

    def test_flat_map_empty_list(self):
        """Test flat_map with empty list."""
        result = flat_map([], lambda x: [x])
        assert result == []

    def test_flat_map_empty_results(self):
        """Test flat_map with mapper returning empty lists."""
        result = flat_map([1, 2, 3], lambda x: [])
        assert result == []


class TestIncludes:
    """Tests for includes function."""

    def test_includes_found(self):
        """Test includes when item is found."""
        assert includes([1, 2, 3], 2) is True

    def test_includes_not_found(self):
        """Test includes when item is not found."""
        assert includes([1, 2, 3], 4) is False

    def test_includes_with_from_index(self):
        """Test includes with from_index parameter."""
        assert includes([1, 2, 3, 2], 2, 2) is True
        assert includes([1, 2, 3, 2], 2, 3) is True
        assert includes([1, 2, 3, 2], 1, 2) is False

    def test_includes_empty_list(self):
        """Test includes with empty list."""
        assert includes([], 1) is False


class TestFindIndex:
    """Tests for find_index function."""

    def test_find_index_found(self):
        """Test find_index when element is found."""
        result = find_index([1, 2, 3, 4], lambda x: x > 2)
        assert result == 2

    def test_find_index_not_found(self):
        """Test find_index when element is not found."""
        result = find_index([1, 2, 3, 4], lambda x: x > 10)
        assert result == -1

    def test_find_index_with_from_index(self):
        """Test find_index with from_index parameter."""
        result = find_index([1, 2, 3, 4, 3], lambda x: x == 3, 3)
        assert result == 4

    def test_find_index_empty_list(self):
        """Test find_index with empty list."""
        result = find_index([], lambda x: True)
        assert result == -1


class TestFindLastIndex:
    """Tests for find_last_index function."""

    def test_find_last_index_found(self):
        """Test find_last_index when element is found."""
        result = find_last_index([1, 2, 3, 2, 4], lambda x: x == 2)
        assert result == 3

    def test_find_last_index_not_found(self):
        """Test find_last_index when element is not found."""
        result = find_last_index([1, 2, 3, 4], lambda x: x > 10)
        assert result == -1

    def test_find_last_index_empty_list(self):
        """Test find_last_index with empty list."""
        result = find_last_index([], lambda x: True)
        assert result == -1


class TestSome:
    """Tests for some function."""

    def test_some_true(self):
        """Test some when at least one element passes."""
        assert some([1, 2, 3, 4], lambda x: x > 3) is True

    def test_some_false(self):
        """Test some when no elements pass."""
        assert some([1, 2, 3, 4], lambda x: x > 10) is False

    def test_some_empty_list(self):
        """Test some with empty list."""
        assert some([], lambda x: True) is False


class TestEvery:
    """Tests for every function."""

    def test_every_true(self):
        """Test every when all elements pass."""
        assert every([2, 4, 6, 8], lambda x: x % 2 == 0) is True

    def test_every_false(self):
        """Test every when not all elements pass."""
        assert every([1, 2, 3, 4], lambda x: x % 2 == 0) is False

    def test_every_empty_list(self):
        """Test every with empty list."""
        assert every([], lambda x: False) is True


class TestAt:
    """Tests for at function."""

    def test_at_positive_index(self):
        """Test at with positive index."""
        assert at([1, 2, 3, 4], 1) == 2

    def test_at_negative_index(self):
        """Test at with negative index."""
        assert at([1, 2, 3, 4], -1) == 4
        assert at([1, 2, 3, 4], -2) == 3

    def test_at_out_of_bounds(self):
        """Test at with out of bounds index."""
        assert at([1, 2, 3, 4], 10) is None
        assert at([1, 2, 3, 4], -10) is None

    def test_at_empty_list(self):
        """Test at with empty list."""
        assert at([], 0) is None


class TestFill:
    """Tests for fill function."""

    def test_fill_entire_array(self):
        """Test fill entire array."""
        arr = [1, 2, 3, 4]
        result = fill(arr, 0)
        assert result == [0, 0, 0, 0]
        assert arr == [0, 0, 0, 0]  # Modified in place

    def test_fill_partial_array(self):
        """Test fill partial array."""
        arr = [1, 2, 3, 4]
        result = fill(arr, 0, 1, 3)
        assert result == [1, 0, 0, 4]
        assert arr == [1, 0, 0, 4]  # Modified in place

    def test_fill_empty_array(self):
        """Test fill empty array."""
        arr = []
        result = fill(arr, 0)
        assert result == []


class TestCopyWithin:
    """Tests for copy_within function."""

    def test_copy_within_basic(self):
        """Test basic copy_within functionality."""
        arr = [1, 2, 3, 4, 5]
        result = copy_within(arr, 0, 3)
        assert result == [4, 5, 3, 4, 5]
        assert arr == [4, 5, 3, 4, 5]  # Modified in place

    def test_copy_within_with_end(self):
        """Test copy_within with end parameter."""
        arr = [1, 2, 3, 4, 5]
        result = copy_within(arr, 2, 0, 2)
        assert result == [1, 2, 1, 2, 5]
        assert arr == [1, 2, 1, 2, 5]  # Modified in place

    def test_copy_within_empty_array(self):
        """Test copy_within with empty array."""
        arr = []
        result = copy_within(arr, 0, 0)
        assert result == []


class TestGroupBy:
    """Tests for group_by function."""

    def test_group_by_first_letter(self):
        """Test group_by with first letter."""
        result = group_by(["apple", "banana", "apricot"], lambda x: x[0])
        expected = {"a": ["apple", "apricot"], "b": ["banana"]}
        assert result == expected

    def test_group_by_modulo(self):
        """Test group_by with modulo operation."""
        result = group_by([1, 2, 3, 4, 5], lambda x: x % 2)
        expected = {1: [1, 3, 5], 0: [2, 4]}
        assert result == expected

    def test_group_by_empty_list(self):
        """Test group_by with empty list."""
        result = group_by([], lambda x: x)
        assert result == {}


class TestToReversed:
    """Tests for to_reversed function."""

    def test_to_reversed_basic(self):
        """Test basic to_reversed functionality."""
        original = [1, 2, 3, 4]
        result = to_reversed(original)
        assert result == [4, 3, 2, 1]
        assert original == [1, 2, 3, 4]  # Original unchanged

    def test_to_reversed_empty_list(self):
        """Test to_reversed with empty list."""
        result = to_reversed([])
        assert result == []

    def test_to_reversed_single_element(self):
        """Test to_reversed with single element."""
        result = to_reversed([1])
        assert result == [1]


class TestToSorted:
    """Tests for to_sorted function."""

    def test_to_sorted_basic(self):
        """Test basic to_sorted functionality."""
        original = [3, 1, 4, 1, 5]
        result = to_sorted(original)
        assert result == [1, 1, 3, 4, 5]
        assert original == [3, 1, 4, 1, 5]  # Original unchanged

    def test_to_sorted_with_key(self):
        """Test to_sorted with key function."""
        result = to_sorted(["banana", "apple", "cherry"], key=len)
        assert result == ["apple", "banana", "cherry"]

    def test_to_sorted_reverse(self):
        """Test to_sorted with reverse parameter."""
        result = to_sorted([1, 2, 3], reverse=True)
        assert result == [3, 2, 1]

    def test_to_sorted_empty_list(self):
        """Test to_sorted with empty list."""
        result = to_sorted([])
        assert result == []


class TestWithItem:
    """Tests for with_item function."""

    def test_with_item_basic(self):
        """Test basic with_item functionality."""
        original = [1, 2, 3, 4]
        result = with_item(original, 1, "two")
        assert result == [1, "two", 3, 4]
        assert original == [1, 2, 3, 4]  # Original unchanged

    def test_with_item_negative_index(self):
        """Test with_item with negative index."""
        result = with_item([1, 2, 3, 4], -1, "last")
        assert result == [1, 2, 3, "last"]

    def test_with_item_out_of_bounds(self):
        """Test with_item with out of bounds index."""
        original = [1, 2, 3]
        result = with_item(original, 10, "new")
        assert result == [1, 2, 3]  # Unchanged


class TestEntries:
    """Tests for entries function."""

    def test_entries_basic(self):
        """Test basic entries functionality."""
        result = entries(["a", "b", "c"])
        assert result == [(0, "a"), (1, "b"), (2, "c")]

    def test_entries_empty_list(self):
        """Test entries with empty list."""
        result = entries([])
        assert result == []


class TestKeys:
    """Tests for keys function."""

    def test_keys_basic(self):
        """Test basic keys functionality."""
        result = keys(["a", "b", "c"])
        assert result == [0, 1, 2]

    def test_keys_empty_list(self):
        """Test keys with empty list."""
        result = keys([])
        assert result == []


class TestValues:
    """Tests for values function."""

    def test_values_basic(self):
        """Test basic values functionality."""
        original = ["a", "b", "c"]
        result = values(original)
        assert result == ["a", "b", "c"]
        assert result is not original  # Different object

    def test_values_empty_list(self):
        """Test values with empty list."""
        result = values([])
        assert result == []


class TestSplice:
    """Tests for splice function."""

    def test_splice_remove_and_insert(self):
        """Test splice removing and inserting elements."""
        arr = [1, 2, 3, 4, 5]
        removed = splice(arr, 2, 1, "a", "b")
        assert arr == [1, 2, "a", "b", 4, 5]
        assert removed == [3]

    def test_splice_only_remove(self):
        """Test splice only removing elements."""
        arr = [1, 2, 3, 4, 5]
        removed = splice(arr, 1, 2)
        assert arr == [1, 4, 5]
        assert removed == [2, 3]

    def test_splice_only_insert(self):
        """Test splice only inserting elements."""
        arr = [1, 2, 3]
        removed = splice(arr, 1, 0, "a", "b")
        assert arr == [1, "a", "b", 2, 3]
        assert removed == []

    def test_splice_negative_start(self):
        """Test splice with negative start index."""
        arr = [1, 2, 3, 4, 5]
        removed = splice(arr, -2, 1, "x")
        assert arr == [1, 2, 3, "x", 5]
        assert removed == [4]

    def test_splice_empty_array(self):
        """Test splice with empty array."""
        arr = []
        removed = splice(arr, 0, 0, "a")
        assert arr == ["a"]
        assert removed == []
