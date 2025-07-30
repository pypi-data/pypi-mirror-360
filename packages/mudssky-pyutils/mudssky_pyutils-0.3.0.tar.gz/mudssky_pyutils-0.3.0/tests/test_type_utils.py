"""Tests for type utility functions."""

import datetime
import math
import re
from decimal import Decimal

from pyutils.type_utils import (
    is_array,
    is_boolean,
    is_date,
    is_empty,
    is_finite,
    is_function,
    is_integer,
    is_nan,
    is_null,
    is_number,
    is_object,
    is_regex,
    is_string,
    is_undefined,
    parse_float,
    parse_int,
    to_boolean,
    to_number,
    to_string,
    typeof,
)


class TestTypeChecking:
    """Test type checking functions."""

    def test_is_array(self):
        """Test is_array function."""
        # Arrays/lists
        assert is_array([]) is True
        assert is_array([1, 2, 3]) is True
        assert is_array([]) is True

        # Tuples (also considered arrays)
        assert is_array(()) is True
        assert is_array((1, 2, 3)) is True

        # Not arrays
        assert is_array("string") is False
        assert is_array({}) is False
        assert is_array(set()) is False
        assert is_array(123) is False
        assert is_array(None) is False

    def test_is_string(self):
        """Test is_string function."""
        # Strings
        assert is_string("") is True
        assert is_string("hello") is True
        assert is_string("") is True

        # Not strings
        assert is_string(123) is False
        assert is_string([]) is False
        assert is_string({}) is False
        assert is_string(None) is False
        assert is_string(True) is False

    def test_is_number(self):
        """Test is_number function."""
        # Numbers
        assert is_number(0) is True
        assert is_number(123) is True
        assert is_number(-456) is True
        assert is_number(3.14) is True
        assert is_number(-2.5) is True
        assert is_number(Decimal("10.5")) is True

        # Special numeric values
        assert is_number(float("inf")) is True
        assert is_number(float("-inf")) is True
        assert is_number(float("nan")) is True

        # Not numbers
        assert is_number("123") is False
        assert is_number([]) is False
        assert is_number({}) is False
        assert is_number(None) is False
        assert is_number(True) is False

    def test_is_boolean(self):
        """Test is_boolean function."""
        # Booleans
        assert is_boolean(True) is True
        assert is_boolean(False) is True

        # Not booleans
        assert is_boolean(1) is False
        assert is_boolean(0) is False
        assert is_boolean("true") is False
        assert is_boolean([]) is False
        assert is_boolean(None) is False

    def test_is_null(self):
        """Test is_null function."""
        # Null values
        assert is_null(None) is True

        # Not null
        assert is_null(0) is False
        assert is_null("") is False
        assert is_null([]) is False
        assert is_null(False) is False

    def test_is_undefined(self):
        """Test is_undefined function."""
        # In Python, we consider None as undefined
        assert is_undefined(None) is True

        # Everything else is defined
        assert is_undefined(0) is False
        assert is_undefined("") is False
        assert is_undefined([]) is False
        assert is_undefined(False) is False

    def test_is_function(self):
        """Test is_function function."""

        # Functions
        def test_func():
            pass

        assert is_function(test_func) is True
        assert is_function(lambda x: x) is True
        assert is_function(len) is True
        assert is_function(print) is True

        # Not functions
        assert is_function("function") is False
        assert is_function(123) is False
        assert is_function([]) is False
        assert is_function({}) is False
        assert is_function(None) is False

    def test_is_object(self):
        """Test is_object function."""
        # Objects (dictionaries)
        assert is_object({}) is True
        assert is_object({"key": "value"}) is True
        assert is_object({}) is True

        # Not objects
        assert is_object([]) is False
        assert is_object("string") is False
        assert is_object(123) is False
        assert is_object(None) is False
        assert is_object(True) is False

    def test_is_date(self):
        """Test is_date function."""
        # Date objects
        assert is_date(datetime.datetime.now()) is True
        assert is_date(datetime.date.today()) is True
        assert is_date(datetime.datetime(2023, 1, 1)) is True

        # Not dates
        assert is_date("2023-01-01") is False
        assert is_date(1672531200) is False  # timestamp
        assert is_date([]) is False
        assert is_date({}) is False
        assert is_date(None) is False

    def test_is_regex(self):
        """Test is_regex function."""
        # Regex objects
        assert is_regex(re.compile(r"\d+")) is True
        assert is_regex(re.compile(r"[a-z]+", re.IGNORECASE)) is True

        # Not regex
        assert is_regex(r"\d+") is False  # string pattern
        assert is_regex("pattern") is False
        assert is_regex([]) is False
        assert is_regex({}) is False
        assert is_regex(None) is False

    def test_is_empty(self):
        """Test is_empty function."""
        # Empty values
        assert is_empty(None) is True
        assert is_empty("") is True
        assert is_empty([]) is True
        assert is_empty({}) is True
        assert is_empty(set()) is True
        assert is_empty(()) is True

        # Non-empty values
        assert is_empty("hello") is False
        assert is_empty([1, 2, 3]) is False
        assert is_empty({"key": "value"}) is False
        assert is_empty({1, 2, 3}) is False
        assert is_empty((1, 2)) is False
        assert is_empty(0) is False
        assert is_empty(False) is False

    def test_is_nan(self):
        """Test is_nan function."""
        # NaN values
        assert is_nan(float("nan")) is True
        assert is_nan(math.nan) is True

        # Not NaN
        assert is_nan(0) is False
        assert is_nan(123) is False
        assert is_nan(3.14) is False
        assert is_nan(float("inf")) is False
        assert is_nan("nan") is False
        assert is_nan(None) is False

    def test_is_finite(self):
        """Test is_finite function."""
        # Finite numbers
        assert is_finite(0) is True
        assert is_finite(123) is True
        assert is_finite(-456) is True
        assert is_finite(3.14) is True
        assert is_finite(-2.5) is True

        # Infinite and NaN
        assert is_finite(float("inf")) is False
        assert is_finite(float("-inf")) is False
        assert is_finite(float("nan")) is False

        # Non-numbers
        assert is_finite("123") is False
        assert is_finite(None) is False
        assert is_finite([]) is False

    def test_is_integer(self):
        """Test is_integer function."""
        # Integers
        assert is_integer(0) is True
        assert is_integer(123) is True
        assert is_integer(-456) is True

        # Float integers
        assert is_integer(123.0) is True
        assert is_integer(-456.0) is True

        # Non-integers
        assert is_integer(3.14) is False
        assert is_integer(-2.5) is False
        assert is_integer("123") is False
        assert is_integer(None) is False
        assert is_integer([]) is False


class TestTypeConversion:
    """Test type conversion functions."""

    def test_to_string(self):
        """Test to_string function."""
        # Various types to string
        assert to_string(123) == "123"
        assert to_string(3.14) == "3.14"
        assert to_string(True) == "True"
        assert to_string(False) == "False"
        assert to_string(None) == "None"
        assert to_string([1, 2, 3]) == "[1, 2, 3]"
        assert to_string({"key": "value"}) == "{'key': 'value'}"

        # Already string
        assert to_string("hello") == "hello"
        assert to_string("") == ""

    def test_to_number(self):
        """Test to_number function."""
        # String to number
        assert to_number("123") == 123
        assert to_number("3.14") == 3.14
        assert to_number("-456") == -456
        assert to_number("0") == 0

        # Boolean to number
        assert to_number(True) == 1
        assert to_number(False) == 0

        # Already number
        assert to_number(123) == 123
        assert to_number(3.14) == 3.14

        # Invalid conversions
        assert math.isnan(to_number("invalid"))
        assert math.isnan(to_number(None))
        assert math.isnan(to_number([]))
        assert math.isnan(to_number({}))

    def test_to_boolean(self):
        """Test to_boolean function."""
        # Truthy values
        assert to_boolean(True) is True
        assert to_boolean(1) is True
        assert to_boolean(-1) is True
        assert to_boolean("hello") is True
        assert to_boolean("false") is True  # non-empty string
        assert to_boolean([1, 2, 3]) is True
        assert to_boolean({"key": "value"}) is True

        # Falsy values
        assert to_boolean(False) is False
        assert to_boolean(0) is False
        assert to_boolean("") is False
        assert to_boolean(None) is False
        assert to_boolean([]) is False
        assert to_boolean({}) is False

    def test_parse_int(self):
        """Test parse_int function."""
        # Valid integer strings
        assert parse_int("123") == 123
        assert parse_int("-456") == -456
        assert parse_int("0") == 0

        # With different bases
        assert parse_int("1010", 2) == 10  # binary
        assert parse_int("FF", 16) == 255  # hexadecimal
        assert parse_int("77", 8) == 63  # octal

        # Float strings (should truncate)
        assert parse_int("123.45") == 123
        assert parse_int("-456.78") == -456

        # Invalid strings
        assert math.isnan(parse_int("invalid"))
        assert math.isnan(parse_int(""))
        assert math.isnan(parse_int("abc"))

        # Non-string inputs
        assert parse_int(123) == 123
        assert parse_int(123.45) == 123
        assert math.isnan(parse_int(None))
        assert math.isnan(parse_int([]))

    def test_parse_float(self):
        """Test parse_float function."""
        # Valid float strings
        assert parse_float("123.45") == 123.45
        assert parse_float("-456.78") == -456.78
        assert parse_float("0.0") == 0.0
        assert parse_float("123") == 123.0

        # Scientific notation
        assert parse_float("1.23e2") == 123.0
        assert parse_float("1.23E-2") == 0.0123

        # Invalid strings
        assert math.isnan(parse_float("invalid"))
        assert math.isnan(parse_float(""))
        assert math.isnan(parse_float("abc"))

        # Non-string inputs
        assert parse_float(123) == 123.0
        assert parse_float(123.45) == 123.45
        assert math.isnan(parse_float(None))
        assert math.isnan(parse_float([]))

    def test_typeof(self):
        """Test typeof function."""
        # Basic types
        assert typeof("hello") == "string"
        assert typeof(123) == "number"
        assert typeof(3.14) == "number"
        assert typeof(True) == "boolean"
        assert typeof(False) == "boolean"
        assert typeof(None) == "undefined"

        # Complex types
        assert typeof([1, 2, 3]) == "object"
        assert typeof({"key": "value"}) == "object"
        assert typeof(lambda x: x) == "function"
        assert typeof(len) == "function"

        # Special cases
        assert typeof(datetime.datetime.now()) == "object"
        assert typeof(re.compile(r"\d+")) == "object"

    def test_edge_cases(self):
        """Test edge cases for type utilities."""
        # Empty collections
        assert is_empty(set()) is True
        assert is_empty(frozenset()) is True

        # Complex numbers
        assert is_number(complex(1, 2)) is True
        assert typeof(complex(1, 2)) == "number"

        # Decimal numbers
        assert is_number(Decimal("10.5")) is True
        assert is_finite(Decimal("10.5")) is True

        # Very large numbers
        large_num = 10**100
        assert is_number(large_num) is True
        assert is_finite(large_num) is True
        assert is_integer(large_num) is True
