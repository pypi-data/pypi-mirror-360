#!/usr/bin/env python

"""Tests for object module."""

from pyutils.object import (
    deep_copy,
    flatten_dict,
    get_nested_value,
    invert,
    is_object,
    map_keys,
    map_values,
    merge,
    omit,
    omit_by,
    pick,
    pick_by,
    remove_non_serializable_props,
    safe_json_stringify,
    set_nested_value,
    unflatten_dict,
)


class TestPick:
    """Test pick function."""

    def test_pick_existing_keys(self):
        """Test picking existing keys."""
        obj = {"a": 1, "b": 2, "c": 3}
        result = pick(obj, ["a", "c"])
        assert result == {"a": 1, "c": 3}

    def test_pick_missing_keys(self):
        """Test picking missing keys."""
        obj = {"a": 1, "b": 2}
        result = pick(obj, ["a", "c"])
        assert result == {"a": 1}

    def test_pick_empty_keys(self):
        """Test picking with empty key list."""
        obj = {"a": 1, "b": 2}
        result = pick(obj, [])
        assert result == {}

    def test_pick_empty_object(self):
        """Test picking from empty object."""
        result = pick({}, ["a", "b"])
        assert result == {}

    def test_pick_all_keys(self):
        """Test picking all keys."""
        obj = {"a": 1, "b": 2}
        result = pick(obj, ["a", "b"])
        assert result == {"a": 1, "b": 2}


class TestPickBy:
    """Test pick_by function."""

    def test_pick_by_value_condition(self):
        """Test picking by value condition."""
        obj = {"a": 1, "b": 2, "c": 3}
        result = pick_by(obj, lambda v, k: v > 1)
        assert result == {"b": 2, "c": 3}

    def test_pick_by_key_condition(self):
        """Test picking by key condition."""
        obj = {"apple": 1, "banana": 2, "cherry": 3}
        result = pick_by(obj, lambda v, k: k.startswith("a"))
        assert result == {"apple": 1}

    def test_pick_by_type_condition(self):
        """Test picking by type condition."""
        obj = {"name": "Alice", "age": 25, "active": True}
        result = pick_by(obj, lambda v, k: isinstance(v, str))
        assert result == {"name": "Alice"}

    def test_pick_by_empty_result(self):
        """Test picking by condition with no matches."""
        obj = {"a": 1, "b": 2}
        result = pick_by(obj, lambda v, k: v > 10)
        assert result == {}


class TestOmit:
    """Test omit function."""

    def test_omit_existing_keys(self):
        """Test omitting existing keys."""
        obj = {"a": 1, "b": 2, "c": 3}
        result = omit(obj, ["b"])
        assert result == {"a": 1, "c": 3}

    def test_omit_missing_keys(self):
        """Test omitting missing keys."""
        obj = {"a": 1, "b": 2}
        result = omit(obj, ["c", "d"])
        assert result == {"a": 1, "b": 2}

    def test_omit_empty_keys(self):
        """Test omitting with empty key list."""
        obj = {"a": 1, "b": 2}
        result = omit(obj, [])
        assert result == {"a": 1, "b": 2}

    def test_omit_all_keys(self):
        """Test omitting all keys."""
        obj = {"a": 1, "b": 2}
        result = omit(obj, ["a", "b"])
        assert result == {}


class TestOmitBy:
    """Test omit_by function."""

    def test_omit_by_value_condition(self):
        """Test omitting by value condition."""
        obj = {"a": 1, "b": 2, "c": 3}
        result = omit_by(obj, lambda v, k: v > 1)
        assert result == {"a": 1}

    def test_omit_by_key_condition(self):
        """Test omitting by key condition."""
        obj = {"apple": 1, "banana": 2, "cherry": 3}
        result = omit_by(obj, lambda v, k: k.startswith("b"))
        assert result == {"apple": 1, "cherry": 3}

    def test_omit_by_type_condition(self):
        """Test omitting by type condition."""
        obj = {"name": "Alice", "age": 25, "active": True}
        result = omit_by(
            obj, lambda v, k: isinstance(v, int) and not isinstance(v, bool)
        )
        assert result == {"name": "Alice", "active": True}


class TestMapKeys:
    """Test map_keys function."""

    def test_map_keys_uppercase(self):
        """Test mapping keys to uppercase."""
        obj = {"a": 1, "b": 2}
        result = map_keys(obj, str.upper)
        assert result == {"A": 1, "B": 2}

    def test_map_keys_prefix(self):
        """Test mapping keys with prefix."""
        obj = {1: "one", 2: "two"}
        result = map_keys(obj, lambda x: f"num_{x}")
        assert result == {"num_1": "one", "num_2": "two"}

    def test_map_keys_empty_object(self):
        """Test mapping keys on empty object."""
        result = map_keys({}, str.upper)
        assert result == {}


class TestMapValues:
    """Test map_values function."""

    def test_map_values_multiply(self):
        """Test mapping values with multiplication."""
        obj = {"a": 1, "b": 2}
        result = map_values(obj, lambda x: x * 2)
        assert result == {"a": 2, "b": 4}

    def test_map_values_uppercase(self):
        """Test mapping string values to uppercase."""
        obj = {"name": "alice", "city": "nyc"}
        result = map_values(obj, str.upper)
        assert result == {"name": "ALICE", "city": "NYC"}

    def test_map_values_empty_object(self):
        """Test mapping values on empty object."""
        result = map_values({}, lambda x: x * 2)
        assert result == {}


class TestIsObject:
    """Test is_object function."""

    def test_is_object_dict(self):
        """Test is_object with dictionary."""
        assert is_object({"a": 1}) is True
        assert is_object({}) is True

    def test_is_object_non_dict(self):
        """Test is_object with non-dictionary values."""
        assert is_object([1, 2, 3]) is False
        assert is_object("string") is False
        assert is_object(123) is False
        assert is_object(None) is False
        assert is_object(True) is False


class TestMerge:
    """Test merge function."""

    def test_merge_simple(self):
        """Test merging simple dictionaries."""
        result = merge({"a": 1}, {"b": 2})
        assert result == {"a": 1, "b": 2}

    def test_merge_nested(self):
        """Test merging nested dictionaries."""
        result = merge({"a": {"x": 1}}, {"a": {"y": 2}})
        assert result == {"a": {"x": 1, "y": 2}}

    def test_merge_override(self):
        """Test merging with value override."""
        result = merge({"a": 1}, {"a": 2})
        assert result == {"a": 2}

    def test_merge_multiple(self):
        """Test merging multiple dictionaries."""
        result = merge({"a": 1}, {"b": 2}, {"c": 3})
        assert result == {"a": 1, "b": 2, "c": 3}

    def test_merge_empty(self):
        """Test merging with empty dictionaries."""
        result = merge({}, {"a": 1}, {})
        assert result == {"a": 1}


class TestInvert:
    """Test invert function."""

    def test_invert_simple(self):
        """Test inverting simple dictionary."""
        obj = {"a": 1, "b": 2}
        result = invert(obj)
        assert result == {1: "a", 2: "b"}

    def test_invert_string_values(self):
        """Test inverting dictionary with string values."""
        obj = {"name": "Alice", "city": "NYC"}
        result = invert(obj)
        assert result == {"Alice": "name", "NYC": "city"}

    def test_invert_empty(self):
        """Test inverting empty dictionary."""
        result = invert({})
        assert result == {}


class TestDeepCopy:
    """Test deep_copy function."""

    def test_deep_copy_nested_dict(self):
        """Test deep copying nested dictionary."""
        original = {"a": {"b": {"c": 1}}}
        copied = deep_copy(original)

        assert copied == original
        assert copied is not original
        assert copied["a"] is not original["a"]
        assert copied["a"]["b"] is not original["a"]["b"]

    def test_deep_copy_with_list(self):
        """Test deep copying dictionary with lists."""
        original = {"items": [1, 2, {"nested": 3}]}
        copied = deep_copy(original)

        assert copied == original
        assert copied["items"] is not original["items"]
        assert copied["items"][2] is not original["items"][2]

    def test_deep_copy_simple(self):
        """Test deep copying simple values."""
        assert deep_copy(42) == 42
        assert deep_copy("string") == "string"
        assert deep_copy([1, 2, 3]) == [1, 2, 3]


class TestFlattenDict:
    """Test flatten_dict function."""

    def test_flatten_nested_dict(self):
        """Test flattening nested dictionary."""
        obj = {"a": {"b": {"c": 1}}}
        result = flatten_dict(obj)
        assert result == {"a.b.c": 1}

    def test_flatten_mixed_dict(self):
        """Test flattening mixed dictionary."""
        obj = {"a": 1, "b": {"c": 2, "d": {"e": 3}}}
        result = flatten_dict(obj)
        assert result == {"a": 1, "b.c": 2, "b.d.e": 3}

    def test_flatten_custom_separator(self):
        """Test flattening with custom separator."""
        obj = {"a": {"b": 1}}
        result = flatten_dict(obj, separator="_")
        assert result == {"a_b": 1}

    def test_flatten_with_prefix(self):
        """Test flattening with prefix."""
        obj = {"a": {"b": 1}}
        result = flatten_dict(obj, prefix="root")
        assert result == {"root.a.b": 1}


class TestUnflattenDict:
    """Test unflatten_dict function."""

    def test_unflatten_simple(self):
        """Test unflattening simple dictionary."""
        obj = {"a.b.c": 1}
        result = unflatten_dict(obj)
        assert result == {"a": {"b": {"c": 1}}}

    def test_unflatten_mixed(self):
        """Test unflattening mixed dictionary."""
        obj = {"a": 1, "b.c": 2, "b.d.e": 3}
        result = unflatten_dict(obj)
        assert result == {"a": 1, "b": {"c": 2, "d": {"e": 3}}}

    def test_unflatten_custom_separator(self):
        """Test unflattening with custom separator."""
        obj = {"a_b": 1}
        result = unflatten_dict(obj, separator="_")
        assert result == {"a": {"b": 1}}


class TestGetNestedValue:
    """Test get_nested_value function."""

    def test_get_nested_existing(self):
        """Test getting existing nested value."""
        obj = {"a": {"b": {"c": 1}}}
        result = get_nested_value(obj, "a.b.c")
        assert result == 1

    def test_get_nested_missing(self):
        """Test getting missing nested value."""
        obj = {"a": {"b": 1}}
        result = get_nested_value(obj, "a.b.c")
        assert result is None

    def test_get_nested_with_default(self):
        """Test getting nested value with default."""
        obj = {"a": 1}
        result = get_nested_value(obj, "a.b.c", default="default")
        assert result == "default"

    def test_get_nested_custom_separator(self):
        """Test getting nested value with custom separator."""
        obj = {"a": {"b": 1}}
        result = get_nested_value(obj, "a_b", separator="_")
        assert result == 1


class TestSetNestedValue:
    """Test set_nested_value function."""

    def test_set_nested_new_path(self):
        """Test setting value on new nested path."""
        obj = {}
        result = set_nested_value(obj, "a.b.c", 1)
        assert result == {"a": {"b": {"c": 1}}}

    def test_set_nested_existing_path(self):
        """Test setting value on existing nested path."""
        obj = {"a": {"b": {"c": 1}}}
        result = set_nested_value(obj, "a.b.c", 2)
        assert result == {"a": {"b": {"c": 2}}}

    def test_set_nested_partial_path(self):
        """Test setting value on partially existing path."""
        obj = {"a": {"x": 1}}
        result = set_nested_value(obj, "a.b.c", 2)
        assert result == {"a": {"x": 1, "b": {"c": 2}}}

    def test_set_nested_custom_separator(self):
        """Test setting nested value with custom separator."""
        obj = {}
        result = set_nested_value(obj, "a_b", 1, separator="_")
        assert result == {"a": {"b": 1}}


class TestRemoveNonSerializableProps:
    """Test remove_non_serializable_props function."""

    def test_remove_function(self):
        """Test removing function from dictionary."""
        obj = {"name": "Alice", "func": lambda x: x}
        result = remove_non_serializable_props(obj)
        assert "name" in result
        assert "func" not in result

    def test_keep_serializable(self):
        """Test keeping serializable values."""
        obj = {"string": "text", "number": 42, "boolean": True, "null": None}
        result = remove_non_serializable_props(obj)
        assert result == obj

    def test_nested_cleaning(self):
        """Test cleaning nested structures."""
        obj = {
            "data": {
                "name": "Alice",
                "func": lambda x: x,
                "items": [1, 2, {"valid": True, "func": lambda: None}],
            }
        }
        result = remove_non_serializable_props(obj)
        assert "func" not in result["data"]
        assert result["data"]["name"] == "Alice"
        assert "func" not in result["data"]["items"][2]


class TestSafeJsonStringify:
    """Test safe_json_stringify function."""

    def test_stringify_simple(self):
        """Test stringifying simple object."""
        obj = {"name": "Alice", "age": 25}
        result = safe_json_stringify(obj)
        assert '"name": "Alice"' in result
        assert '"age": 25' in result

    def test_stringify_with_functions(self):
        """Test stringifying object with functions."""
        obj = {"name": "Alice", "func": lambda x: x}
        result = safe_json_stringify(obj)
        assert '"name": "Alice"' in result
        assert "func" not in result

    def test_stringify_with_indent(self):
        """Test stringifying with indentation."""
        obj = {"a": 1}
        result = safe_json_stringify(obj, indent=2)
        assert "\n" in result  # Should have newlines for formatting

    def test_stringify_nested(self):
        """Test stringifying nested object."""
        obj = {"user": {"name": "Alice", "details": {"age": 25}}}
        result = safe_json_stringify(obj)
        assert "Alice" in result
        assert "25" in result
