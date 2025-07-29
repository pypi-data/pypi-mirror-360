#!/usr/bin/env python

"""Tests for array module."""

import pytest

from pyutils.array import (
    alphabetical,
    boil,
    chunk,
    count_by,
    diff,
    first,
    fork,
    has_intersects,
    last,
    max_by,
    min_by,
    range_iter,
    range_list,
    shuffle,
    sum_by,
    toggle,
    unique,
    zip_lists,
    zip_object,
)


class TestChunk:
    """Test chunk function."""

    def test_chunk_basic(self):
        """Test basic chunking."""
        result = chunk([1, 2, 3, 4, 5, 6], 2)
        assert result == [[1, 2], [3, 4], [5, 6]]

    def test_chunk_uneven(self):
        """Test chunking with uneven division."""
        result = chunk([1, 2, 3, 4, 5], 2)
        assert result == [[1, 2], [3, 4], [5]]

    def test_chunk_empty_list(self):
        """Test chunking empty list."""
        result = chunk([], 2)
        assert result == []

    def test_chunk_size_larger_than_list(self):
        """Test chunk size larger than list."""
        result = chunk([1, 2], 5)
        assert result == [[1, 2]]

    def test_chunk_size_zero(self):
        """Test chunk with size zero."""
        with pytest.raises(ValueError):
            chunk([1, 2, 3], 0)

    def test_chunk_size_negative(self):
        """Test chunk with negative size."""
        with pytest.raises(ValueError):
            chunk([1, 2, 3], -1)


class TestUnique:
    """Test unique function."""

    def test_unique_basic(self):
        """Test basic unique operation."""
        result = unique([1, 2, 2, 3, 3, 3])
        assert result == [1, 2, 3]

    def test_unique_preserve_order(self):
        """Test that unique preserves order."""
        result = unique([3, 1, 2, 1, 3])
        assert result == [3, 1, 2]

    def test_unique_empty_list(self):
        """Test unique with empty list."""
        result = unique([])
        assert result == []

    def test_unique_single_element(self):
        """Test unique with single element."""
        result = unique([1])
        assert result == [1]

    def test_unique_strings(self):
        """Test unique with strings."""
        result = unique(["a", "b", "a", "c", "b"])
        assert result == ["a", "b", "c"]


class TestShuffle:
    """Test shuffle function."""

    def test_shuffle_preserves_elements(self):
        """Test that shuffle preserves all elements."""
        original = [1, 2, 3, 4, 5]
        result = shuffle(original.copy())
        assert sorted(result) == sorted(original)
        assert len(result) == len(original)

    def test_shuffle_empty_list(self):
        """Test shuffle with empty list."""
        result = shuffle([])
        assert result == []

    def test_shuffle_single_element(self):
        """Test shuffle with single element."""
        result = shuffle([1])
        assert result == [1]


class TestDiff:
    """Test diff function."""

    def test_diff_basic(self):
        """Test basic diff operation."""
        result = diff([1, 2, 3, 4], [2, 4])
        assert result == [1, 3]

    def test_diff_no_difference(self):
        """Test diff when no difference."""
        result = diff([1, 2, 3], [1, 2, 3])
        assert result == []

    def test_diff_empty_lists(self):
        """Test diff with empty lists."""
        assert diff([], []) == []
        assert diff([1, 2], []) == [1, 2]
        assert diff([], [1, 2]) == []

    def test_diff_duplicates(self):
        """Test diff with duplicates."""
        result = diff([1, 1, 2, 3], [1])
        assert result == [2, 3]


class TestFork:
    """Test fork function."""

    def test_fork_basic(self):
        """Test basic fork operation."""
        result = fork([1, 2, 3, 4, 5], lambda x: x % 2 == 0)
        assert result == ([2, 4], [1, 3, 5])

    def test_fork_all_true(self):
        """Test fork when all elements match condition."""
        result = fork([2, 4, 6], lambda x: x % 2 == 0)
        assert result == ([2, 4, 6], [])

    def test_fork_all_false(self):
        """Test fork when no elements match condition."""
        result = fork([1, 3, 5], lambda x: x % 2 == 0)
        assert result == ([], [1, 3, 5])

    def test_fork_empty_list(self):
        """Test fork with empty list."""
        result = fork([], lambda x: x > 0)
        assert result == ([], [])


class TestZipObject:
    """Test zip_object function."""

    def test_zip_object_basic(self):
        """Test basic zip_object operation."""
        result = zip_object(["a", "b", "c"], [1, 2, 3])
        assert result == {"a": 1, "b": 2, "c": 3}

    def test_zip_object_unequal_lengths(self):
        """Test zip_object with unequal length lists."""
        result = zip_object(["a", "b"], [1, 2, 3])
        assert result == {"a": 1, "b": 2}

    def test_zip_object_empty_lists(self):
        """Test zip_object with empty lists."""
        result = zip_object([], [])
        assert result == {}

    def test_zip_object_keys_longer(self):
        """Test zip_object when keys list is longer."""
        result = zip_object(["a", "b", "c"], [1, 2])
        assert result == {"a": 1, "b": 2}


class TestRangeList:
    """Test range_list function."""

    def test_range_list_basic(self):
        """Test basic range_list operation."""
        result = range_list(0, 5)
        assert result == [0, 1, 2, 3, 4]

    def test_range_list_with_step(self):
        """Test range_list with step."""
        result = range_list(0, 10, 2)
        assert result == [0, 2, 4, 6, 8]

    def test_range_list_negative_step(self):
        """Test range_list with negative step."""
        result = range_list(5, 0, -1)
        assert result == [5, 4, 3, 2, 1]

    def test_range_list_empty_range(self):
        """Test range_list with empty range."""
        result = range_list(5, 5)
        assert result == []


class TestRangeIter:
    """Test range_iter function."""

    def test_range_iter_basic(self):
        """Test basic range_iter operation."""
        result = list(range_iter(0, 5))
        assert result == [0, 1, 2, 3, 4]

    def test_range_iter_with_step(self):
        """Test range_iter with step."""
        result = list(range_iter(0, 10, 2))
        assert result == [0, 2, 4, 6, 8]

    def test_range_iter_is_iterator(self):
        """Test that range_iter returns an iterator."""
        result = range_iter(0, 3)
        assert hasattr(result, "__iter__")
        assert hasattr(result, "__next__")


class TestBoil:
    """Test boil function."""

    def test_boil_sum(self):
        """Test boil for sum operation."""
        result = boil([1, 2, 3, 4], lambda acc, x: acc + x, 0)
        assert result == 10

    def test_boil_product(self):
        """Test boil for product operation."""
        result = boil([1, 2, 3, 4], lambda acc, x: acc * x, 1)
        assert result == 24

    def test_boil_empty_list(self):
        """Test boil with empty list."""
        result = boil([], lambda acc, x: acc + x, 5)
        assert result == 5

    def test_boil_string_concatenation(self):
        """Test boil for string concatenation."""
        result = boil(["a", "b", "c"], lambda acc, x: acc + x, "")
        assert result == "abc"


class TestCountBy:
    """Test count_by function."""

    def test_count_by_basic(self):
        """Test basic count_by operation."""
        result = count_by([1, 2, 3, 4, 5], lambda x: x % 2)
        assert result == {1: 3, 0: 2}  # odd: 3, even: 2

    def test_count_by_strings(self):
        """Test count_by with strings."""
        result = count_by(["apple", "banana", "apricot"], lambda x: x[0])
        assert result == {"a": 2, "b": 1}

    def test_count_by_empty_list(self):
        """Test count_by with empty list."""
        result = count_by([], lambda x: x)
        assert result == {}


class TestFirst:
    """Test first function."""

    def test_first_basic(self):
        """Test basic first operation."""
        result = first([1, 2, 3, 4])
        assert result == 1

    def test_first_empty_list(self):
        """Test first with empty list."""
        result = first([])
        assert result is None

    def test_first_with_default(self):
        """Test first with default value."""
        result = first([], "default")
        assert result == "default"


class TestLast:
    """Test last function."""

    def test_last_basic(self):
        """Test basic last operation."""
        result = last([1, 2, 3, 4])
        assert result == 4

    def test_last_empty_list(self):
        """Test last with empty list."""
        result = last([])
        assert result is None

    def test_last_with_default(self):
        """Test last with default value."""
        result = last([], "default")
        assert result == "default"


class TestHasIntersects:
    """Test has_intersects function."""

    def test_has_intersects_true(self):
        """Test has_intersects when lists intersect."""
        result = has_intersects([1, 2, 3], [3, 4, 5])
        assert result is True

    def test_has_intersects_false(self):
        """Test has_intersects when lists don't intersect."""
        result = has_intersects([1, 2, 3], [4, 5, 6])
        assert result is False

    def test_has_intersects_empty_lists(self):
        """Test has_intersects with empty lists."""
        assert has_intersects([], [1, 2, 3]) is False
        assert has_intersects([1, 2, 3], []) is False
        assert has_intersects([], []) is False


class TestMaxBy:
    """Test max_by function."""

    def test_max_by_basic(self):
        """Test basic max_by operation."""
        result = max_by([1, 2, 3, 4, 5], lambda x: -x)
        assert result == 1  # minimum value when using negative

    def test_max_by_strings(self):
        """Test max_by with strings."""
        result = max_by(["apple", "banana", "cherry"], len)
        assert result == "banana"

    def test_max_by_empty_list(self):
        """Test max_by with empty list."""
        result = max_by([], lambda x: x)
        assert result is None


class TestMinBy:
    """Test min_by function."""

    def test_min_by_basic(self):
        """Test basic min_by operation."""
        result = min_by([1, 2, 3, 4, 5], lambda x: -x)
        assert result == 5  # maximum value when using negative

    def test_min_by_strings(self):
        """Test min_by with strings."""
        result = min_by(["apple", "banana", "cherry"], len)
        assert result == "apple"

    def test_min_by_empty_list(self):
        """Test min_by with empty list."""
        result = min_by([], lambda x: x)
        assert result is None


class TestToggle:
    """Test toggle function."""

    def test_toggle_add_element(self):
        """Test toggle adding element."""
        result = toggle([1, 2, 3], 4)
        assert result == [1, 2, 3, 4]

    def test_toggle_remove_element(self):
        """Test toggle removing element."""
        result = toggle([1, 2, 3], 2)
        assert result == [1, 3]

    def test_toggle_empty_list(self):
        """Test toggle with empty list."""
        result = toggle([], 1)
        assert result == [1]


class TestSumBy:
    """Test sum_by function."""

    def test_sum_by_basic(self):
        """Test basic sum_by operation."""
        result = sum_by([1, 2, 3, 4, 5], lambda x: x * 2)
        assert result == 30  # (1+2+3+4+5) * 2

    def test_sum_by_strings(self):
        """Test sum_by with string lengths."""
        result = sum_by(["a", "bb", "ccc"], len)
        assert result == 6

    def test_sum_by_empty_list(self):
        """Test sum_by with empty list."""
        result = sum_by([], lambda x: x)
        assert result == 0


class TestZipLists:
    """Test zip_lists function."""

    def test_zip_lists_basic(self):
        """Test basic zip_lists operation."""
        result = zip_lists([1, 2, 3], ["a", "b", "c"])
        assert result == [(1, "a"), (2, "b"), (3, "c")]

    def test_zip_lists_unequal_lengths(self):
        """Test zip_lists with unequal lengths."""
        result = zip_lists([1, 2], ["a", "b", "c"])
        assert result == [(1, "a"), (2, "b")]

    def test_zip_lists_empty(self):
        """Test zip_lists with empty lists."""
        result = zip_lists([], [])
        assert result == []


class TestAlphabetical:
    """Test alphabetical function."""

    def test_alphabetical_basic(self):
        """Test basic alphabetical sorting."""
        result = alphabetical(["banana", "apple", "cherry"])
        assert result == ["apple", "banana", "cherry"]

    def test_alphabetical_case_insensitive(self):
        """Test alphabetical case insensitive sorting."""
        result = alphabetical(["Banana", "apple", "Cherry"])
        assert result == ["apple", "Banana", "Cherry"]

    def test_alphabetical_empty_list(self):
        """Test alphabetical with empty list."""
        result = alphabetical([])
        assert result == []

    def test_alphabetical_single_element(self):
        """Test alphabetical with single element."""
        result = alphabetical(["apple"])
        assert result == ["apple"]
