"""Top-level package for pyutils.

A comprehensive Python utility library providing functions for array manipulation,
string processing, mathematical operations, object handling, function utilities,
asynchronous operations, and byte processing.

Ported from the jsutils JavaScript library to provide similar functionality in Python.
"""

__author__ = """mudssky"""
__email__ = "mudssky@gmail.com"
__version__ = "0.1.0"

# Import all modules
from . import array, async_utils, function, math, object, string
from . import bytes as bytes_utils

# Import commonly used functions for convenience
from .array import (
    alphabetical,
    chunk,
    diff,
    first,
    has_intersects,
    last,
    range_iter,
    range_list,
    shuffle,
    toggle,
    unique,
    zip_object,
)
from .async_utils import (
    delay,
    filter_async,
    map_async,
    race,
    retry_async,
    run_in_thread,
    sleep_async,
    timeout,
)
from .bytes import (
    Bytes,
    bytes_util,
    humanize_bytes,
    parse_bytes,
)
from .function import (
    debounce,
    memoize,
    once,
    throttle,
    with_retry,
)
from .math import (
    clamp,
    factorial,
    fibonacci,
    gcd,
    get_random_int,
    is_even,
    is_odd,
    is_prime,
    lcm,
    lerp,
    normalize,
)
from .object import (
    deep_copy,
    flatten_dict,
    get_nested_value,
    merge,
    omit,
    pick,
    safe_json_stringify,
    set_nested_value,
)
from .string import (
    camel_case,
    capitalize,
    dash_case,
    fuzzy_match,
    generate_uuid,
    parse_template,
    pascal_case,
    slugify,
    snake_case,
    trim,
    truncate,
)


# Define what gets exported when using "from pyutils import *"
__all__ = [
    "Bytes",
    "alphabetical",
    "array",
    "async_utils",
    "bytes_util",
    "bytes_utils",
    "camel_case",
    "capitalize",
    "chunk",
    "clamp",
    "dash_case",
    "debounce",
    "deep_copy",
    "delay",
    "diff",
    "factorial",
    "fibonacci",
    "filter_async",
    "first",
    "flatten_dict",
    "function",
    "fuzzy_match",
    "gcd",
    "generate_uuid",
    "get_nested_value",
    "get_random_int",
    "has_intersects",
    "humanize_bytes",
    "is_even",
    "is_odd",
    "is_prime",
    "last",
    "lcm",
    "lerp",
    "map_async",
    "math",
    "memoize",
    "merge",
    "normalize",
    "object",
    "omit",
    "once",
    "parse_bytes",
    "parse_template",
    "pascal_case",
    "pick",
    "race",
    "range_iter",
    "range_list",
    "retry_async",
    "run_in_thread",
    "safe_json_stringify",
    "set_nested_value",
    "shuffle",
    "sleep_async",
    "slugify",
    "snake_case",
    "string",
    "throttle",
    "timeout",
    "toggle",
    "trim",
    "truncate",
    "unique",
    "with_retry",
    "zip_object",
]
