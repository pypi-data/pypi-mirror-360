"""Type utility functions.

This module provides utility functions for type checking and conversion,
porting JavaScript type checking methods and other type utilities to Python.
"""

import re
from typing import Any


def is_array(value: Any) -> bool:
    """Check if value is an array (list or tuple).

    Args:
        value: Value to check

    Returns:
        True if value is a list or tuple, False otherwise

    Examples:
        >>> is_array([1, 2, 3])
        True
        >>> is_array((1, 2, 3))
        True
        >>> is_array('string')
        False
    """
    return isinstance(value, list | tuple)


def is_string(value: Any) -> bool:
    """Check if value is a string.

    Args:
        value: Value to check

    Returns:
        True if value is a string, False otherwise

    Examples:
        >>> is_string('hello')
        True
        >>> is_string(123)
        False
    """
    return isinstance(value, str)


def is_number(value: Any) -> bool:
    """Check if value is a number (int or float).

    Args:
        value: Value to check

    Returns:
        True if value is a number, False otherwise

    Examples:
        >>> is_number(123)
        True
        >>> is_number(3.14)
        True
        >>> is_number('123')
        False
    """
    from decimal import Decimal

    return isinstance(value, int | float | complex | Decimal) and not isinstance(
        value, bool
    )


def is_boolean(value: Any) -> bool:
    """Check if value is a boolean.

    Args:
        value: Value to check

    Returns:
        True if value is a boolean, False otherwise

    Examples:
        >>> is_boolean(True)
        True
        >>> is_boolean(False)
        True
        >>> is_boolean(1)
        False
    """
    return isinstance(value, bool)


def is_null(value: Any) -> bool:
    """Check if value is None (null in JavaScript).

    Args:
        value: Value to check

    Returns:
        True if value is None, False otherwise

    Examples:
        >>> is_null(None)
        True
        >>> is_null(0)
        False
        >>> is_null('')
        False
    """
    return value is None


def is_undefined(value: Any) -> bool:
    """Check if value is undefined (similar to JavaScript undefined).

    In Python context, this checks for None or missing attributes.

    Args:
        value: Value to check

    Returns:
        True if value is None, False otherwise

    Examples:
        >>> is_undefined(None)
        True
        >>> is_undefined(0)
        False
    """
    return value is None


def is_function(value: Any) -> bool:
    """Check if value is a function or callable.

    Args:
        value: Value to check

    Returns:
        True if value is callable, False otherwise

    Examples:
        >>> is_function(lambda x: x)
        True
        >>> is_function(print)
        True
        >>> is_function('string')
        False
    """
    return callable(value)


def is_object(value: Any) -> bool:
    """Check if value is an object (dict in Python).

    Args:
        value: Value to check

    Returns:
        True if value is a dict, False otherwise

    Examples:
        >>> is_object({'key': 'value'})
        True
        >>> is_object([])
        False
        >>> is_object('string')
        False
    """
    return isinstance(value, dict)


def is_date(value: Any) -> bool:
    """Check if value is a date/datetime object.

    Args:
        value: Value to check

    Returns:
        True if value is a date or datetime, False otherwise

    Examples:
        >>> import datetime
        >>> is_date(datetime.datetime.now())
        True
        >>> is_date(datetime.date.today())
        True
        >>> is_date('2023-01-01')
        False
    """
    import datetime

    return isinstance(value, datetime.date | datetime.datetime)


def is_regex(value: Any) -> bool:
    r"""Check if value is a compiled regular expression.

    Args:
        value: Value to check

    Returns:
        True if value is a compiled regex, False otherwise

    Examples:
        >>> import re
        >>> is_regex(re.compile(r'\d+'))
        True
        >>> is_regex(r'\d+')
        False
    """
    return isinstance(value, re.Pattern)


def is_empty(value: Any) -> bool:
    """Check if value is empty (like JavaScript's concept of empty).

    Args:
        value: Value to check

    Returns:
        True if value is empty, False otherwise

    Examples:
        >>> is_empty('')
        True
        >>> is_empty([])
        True
        >>> is_empty({})
        True
        >>> is_empty(set())
        True
        >>> is_empty(frozenset())
        True
        >>> is_empty(None)
        True
        >>> is_empty(0)
        False
    """
    if value is None:
        return True
    if isinstance(value, str | list | tuple | dict | set | frozenset):
        return len(value) == 0
    return False


def is_nan(value: Any) -> bool:
    """Check if value is NaN (Not a Number).

    Args:
        value: Value to check

    Returns:
        True if value is NaN, False otherwise

    Examples:
        >>> is_nan(float('nan'))
        True
        >>> is_nan(123)
        False
        >>> is_nan('string')
        False
    """
    try:
        return isinstance(value, float) and value != value  # NaN != NaN
    except Exception:
        return False


def is_finite(value: Any) -> bool:
    """Check if value is a finite number.

    Args:
        value: Value to check

    Returns:
        True if value is a finite number, False otherwise

    Examples:
        >>> is_finite(123)
        True
        >>> is_finite(3.14)
        True
        >>> is_finite(float('inf'))
        False
        >>> is_finite(float('nan'))
        False
    """
    import math
    from decimal import Decimal

    try:
        if isinstance(value, int | float):
            return math.isfinite(value)
        elif isinstance(value, Decimal):
            return value.is_finite()
        return False
    except Exception:
        return False


def is_integer(value: Any) -> bool:
    """Check if value is an integer (like JavaScript Number.isInteger).

    Args:
        value: Value to check

    Returns:
        True if value is an integer, False otherwise

    Examples:
        >>> is_integer(123)
        True
        >>> is_integer(3.0)
        True
        >>> is_integer(3.14)
        False
        >>> is_integer('123')
        False
    """
    if isinstance(value, bool):
        return False
    if isinstance(value, int):
        return True
    if isinstance(value, float):
        return value.is_integer()
    return False


def to_string(value: Any) -> str:
    """Convert value to string (like JavaScript String() constructor).

    Args:
        value: Value to convert

    Returns:
        String representation of value

    Examples:
        >>> to_string(123)
        '123'
        >>> to_string(True)
        'True'
        >>> to_string([1, 2, 3])
        '[1, 2, 3]'
    """
    if value is None:
        return "None"
    return str(value)


def to_number(value: Any) -> int | float:
    """Convert value to number (like JavaScript Number() constructor).

    Args:
        value: Value to convert

    Returns:
        Number representation of value, or NaN if conversion fails

    Examples:
        >>> to_number('123')
        123
        >>> to_number('3.14')
        3.14
        >>> import math
        >>> math.isnan(to_number('invalid'))
        True
        >>> to_number(True)
        1
    """
    if isinstance(value, int | float):
        return value
    if isinstance(value, bool):
        return 1 if value else 0
    if isinstance(value, str):
        value = value.strip()
        if not value:
            return 0
        try:
            # Try integer first
            if "." not in value and "e" not in value.lower():
                return int(value)
            return float(value)
        except ValueError:
            return float("nan")
    return float("nan")


def to_boolean(value: Any) -> bool:
    """Convert value to boolean (like JavaScript Boolean() constructor).

    Args:
        value: Value to convert

    Returns:
        Boolean representation of value

    Examples:
        >>> to_boolean(1)
        True
        >>> to_boolean(0)
        False
        >>> to_boolean('')
        False
        >>> to_boolean('hello')
        True
        >>> to_boolean([])
        False
    """
    if value is None:
        return False
    if isinstance(value, bool):
        return value
    if isinstance(value, int | float):
        return value != 0 and not is_nan(value)
    if isinstance(value, str):
        return len(value) > 0
    if isinstance(value, list | tuple | dict | set):
        return len(value) > 0
    return bool(value)


def parse_int(value: Any, radix: int = 10) -> int | float:
    """Parse string to integer (like JavaScript parseInt).

    Args:
        value: String to parse
        radix: Base for parsing (2-36), defaults to 10

    Returns:
        Parsed integer or NaN if parsing fails

    Examples:
        >>> parse_int('123')
        123
        >>> parse_int('123.45')
        123
        >>> parse_int('ff', 16)
        255
        >>> import math
        >>> math.isnan(parse_int('invalid'))
        True
    """
    if not isinstance(value, str):
        if isinstance(value, int | float):
            return int(value)
        return float("nan")

    value = value.strip()
    if not value:
        return float("nan")

    # Handle sign
    sign = 1
    if value.startswith("-"):
        sign = -1
        value = value[1:]
    elif value.startswith("+"):
        value = value[1:]

    # Extract valid characters for the given radix
    valid_chars = "0123456789abcdefghijklmnopqrstuvwxyz"[:radix]
    result = ""

    for char in value.lower():
        if char in valid_chars:
            result += char
        else:
            break

    if not result:
        return float("nan")

    try:
        return sign * int(result, radix)
    except ValueError:
        return float("nan")


def parse_float(value: Any) -> float:
    """Parse string to float (like JavaScript parseFloat).

    Args:
        value: String to parse

    Returns:
        Parsed float or NaN if parsing fails

    Examples:
        >>> parse_float('3.14')
        3.14
        >>> parse_float('3.14abc')
        3.14
        >>> import math
        >>> math.isnan(parse_float('abc'))
        True
    """
    if not isinstance(value, str):
        if isinstance(value, int | float):
            return float(value)
        return float("nan")

    value = value.strip()
    if not value:
        return float("nan")

    # Extract valid float characters from the beginning
    import re

    match = re.match(r"^[+-]?\d*\.?\d*([eE][+-]?\d+)?", value)
    if match:
        float_str = match.group(0)
        if float_str and float_str not in ["+", "-", "."]:
            try:
                return float(float_str)
            except ValueError:
                pass

    return float("nan")


def typeof(value: Any) -> str:
    """Get type of value (like JavaScript typeof operator).

    Args:
        value: Value to check type of

    Returns:
        Type string

    Examples:
        >>> typeof('hello')
        'string'
        >>> typeof(123)
        'number'
        >>> typeof(True)
        'boolean'
        >>> typeof(None)
        'undefined'
        >>> typeof({})
        'object'
        >>> typeof([])
        'object'
        >>> typeof(lambda x: x)
        'function'
    """
    from decimal import Decimal

    if value is None:
        return "undefined"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, str):
        return "string"
    if isinstance(value, int | float | complex | Decimal):
        return "number"
    if callable(value):
        return "function"
    return "object"
