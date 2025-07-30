"""Encoding and decoding utility functions.

This module provides utility functions for encoding and decoding,
porting JavaScript encoding methods and other encoding utilities to Python.
"""

import base64
import html
import json
import urllib.parse
from typing import Any


def btoa(data: str) -> str:
    """Encode string to base64 (like JavaScript btoa).

    Args:
        data: String to encode

    Returns:
        Base64 encoded string

    Examples:
        >>> btoa('hello')
        'aGVsbG8='
        >>> btoa('Hello, World!')
        'SGVsbG8sIFdvcmxkIQ=='
    """
    return base64.b64encode(data.encode("utf-8")).decode("ascii")


def atob(data: str) -> str:
    """Decode base64 string (like JavaScript atob).

    Args:
        data: Base64 string to decode

    Returns:
        Decoded string

    Raises:
        ValueError: If input is not valid base64

    Examples:
        >>> atob('aGVsbG8=')
        'hello'
        >>> atob('SGVsbG8sIFdvcmxkIQ==')
        'Hello, World!'
    """
    try:
        return base64.b64decode(data).decode("utf-8")
    except Exception as e:
        raise ValueError(f"Invalid base64 string: {e}") from e


def escape_html(text: str) -> str:
    """Escape HTML special characters.

    Args:
        text: Text to escape

    Returns:
        HTML escaped text

    Examples:
        >>> escape_html('<div>Hello & goodbye</div>')
        '&lt;div&gt;Hello &amp; goodbye&lt;/div&gt;'
        >>> escape_html('"quoted" text')
        '&quot;quoted&quot; text'
    """
    return html.escape(text, quote=True)


def unescape_html(text: str) -> str:
    """Unescape HTML entities.

    Args:
        text: HTML text to unescape

    Returns:
        Unescaped text

    Examples:
        >>> unescape_html('&lt;div&gt;Hello &amp; goodbye&lt;/div&gt;')
        '<div>Hello & goodbye</div>'
        >>> unescape_html('&quot;quoted&quot; text')
        '"quoted" text'
    """
    return html.unescape(text)


def encode_base64(data: str | bytes) -> str:
    """Encode data to base64.

    Args:
        data: Data to encode (string or bytes)

    Returns:
        Base64 encoded string

    Examples:
        >>> encode_base64('hello world')
        'aGVsbG8gd29ybGQ='
        >>> encode_base64(b'hello world')
        'aGVsbG8gd29ybGQ='
    """
    if isinstance(data, str):
        data = data.encode("utf-8")
    return base64.b64encode(data).decode("ascii")


def decode_base64(data: str) -> str:
    """Decode base64 string to string.

    Args:
        data: Base64 string to decode

    Returns:
        Decoded string

    Raises:
        ValueError: If input is not valid base64

    Examples:
        >>> decode_base64('aGVsbG8gd29ybGQ=')
        'hello world'
    """
    try:
        return base64.b64decode(data).decode("utf-8")
    except Exception as e:
        raise ValueError(f"Invalid base64 string: {e}") from e


def encode_hex(data: str | bytes) -> str:
    """Encode data to hexadecimal.

    Args:
        data: Data to encode (string or bytes)

    Returns:
        Hexadecimal encoded string

    Examples:
        >>> encode_hex('hello')
        '68656c6c6f'
        >>> encode_hex(b'hello')
        '68656c6c6f'
    """
    if isinstance(data, str):
        data = data.encode("utf-8")
    return data.hex()


def decode_hex(data: str) -> str:
    """Decode hexadecimal string to string.

    Args:
        data: Hexadecimal string to decode

    Returns:
        Decoded string

    Raises:
        ValueError: If input is not valid hexadecimal

    Examples:
        >>> decode_hex('68656c6c6f')
        'hello'
    """
    if not data:
        return ""
    try:
        return bytes.fromhex(data).decode("utf-8")
    except ValueError as e:
        raise ValueError(f"Invalid hexadecimal string: {e}") from e
    except UnicodeDecodeError as e:
        raise ValueError(f"Invalid UTF-8 in hexadecimal data: {e}") from e


def json_stringify(obj: Any, indent: int | None = None) -> str:
    """Convert object to JSON string (like JavaScript JSON.stringify).

    Args:
        obj: Object to convert
        indent: Indentation for pretty printing

    Returns:
        JSON string

    Examples:
        >>> json_stringify({'name': 'John', 'age': 30})
        '{"name": "John", "age": 30}'
        >>> json_stringify([1, 2, 3])
        '[1, 2, 3]'
    """
    try:
        return json.dumps(obj, indent=indent, ensure_ascii=False)
    except TypeError:
        # Handle non-serializable objects
        return json.dumps(str(obj), indent=indent)


def json_parse(text: str) -> Any:
    """Parse JSON string to object (like JavaScript JSON.parse).

    Args:
        text: JSON string to parse

    Returns:
        Parsed object

    Raises:
        ValueError: If input is not valid JSON

    Examples:
        >>> json_parse('{"name": "John", "age": 30}')
        {'name': 'John', 'age': 30}
        >>> json_parse('[1, 2, 3]')
        [1, 2, 3]
    """
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON string: {e}") from e


def url_encode(text: str) -> str:
    """URL encode a string (like JavaScript encodeURIComponent).

    Args:
        text: String to encode

    Returns:
        URL encoded string

    Examples:
        >>> url_encode('hello world')
        'hello%20world'
        >>> url_encode('user@example.com')
        'user%40example.com'
    """
    return urllib.parse.quote(text)


def url_decode(text: str) -> str:
    """URL decode a string (like JavaScript decodeURIComponent).

    Args:
        text: String to decode

    Returns:
        URL decoded string

    Examples:
        >>> url_decode('hello%20world')
        'hello world'
        >>> url_decode('user%40example.com')
        'user@example.com'
    """
    return urllib.parse.unquote(text)


def escape_regex(text: str) -> str:
    r"""Escape special regex characters in a string.

    Args:
        text: String to escape

    Returns:
        Escaped string safe for use in regex

    Examples:
        >>> escape_regex('hello.world')
        'hello\\.world'
        >>> escape_regex('$100 (USD)')
        '\\$100 \\(USD\\)'
    """
    import re

    return re.escape(text)


def hash_string(text: str, algorithm: str = "sha256") -> str:
    """Generate hash of a string.

    Args:
        text: String to hash
        algorithm: Hash algorithm ('md5', 'sha1', 'sha256', 'sha512')

    Returns:
        Hexadecimal hash string

    Raises:
        ValueError: If algorithm is not supported

    Examples:
        >>> len(hash_string('hello', 'md5'))
        32
        >>> len(hash_string('hello', 'sha256'))
        64
    """
    import hashlib

    algorithms = {
        "md5": hashlib.md5,
        "sha1": hashlib.sha1,
        "sha256": hashlib.sha256,
        "sha512": hashlib.sha512,
    }

    if algorithm not in algorithms:
        raise ValueError(
            f"Unsupported algorithm: {algorithm}. Supported: {list(algorithms.keys())}"
        )

    hasher = algorithms[algorithm]()
    hasher.update(text.encode("utf-8"))
    return hasher.hexdigest()


def generate_random_string(length: int = 16, charset: str = "alphanumeric") -> str:
    """Generate a random string.

    Args:
        length: Length of the string to generate
        charset: Character set to use ('alphanumeric', 'alpha', 'numeric', 'hex') or
            custom string

    Returns:
        Random string

    Examples:
        >>> len(generate_random_string(10))
        10
        >>> all(c.isalnum() for c in generate_random_string(10, 'alphanumeric'))
        True
    """
    import secrets
    import string

    if length == 0:
        return ""

    charsets = {
        "alphanumeric": string.ascii_letters + string.digits,
        "alpha": string.ascii_letters,
        "numeric": string.digits,
        "hex": "0123456789abcdef",
    }

    # If charset is a predefined name, use it; otherwise treat as custom charset
    if charset in charsets:
        chars = charsets[charset]
    else:
        chars = charset

    return "".join(secrets.choice(chars) for _ in range(length))


def is_base64(text: str) -> bool:
    """Check if a string is valid base64.

    Args:
        text: String to check

    Returns:
        True if valid base64, False otherwise

    Examples:
        >>> is_base64('aGVsbG8=')
        True
        >>> is_base64('hello')
        False
    """
    if not text:
        return False
    try:
        # Check if string is valid base64
        text_bytes = text.encode("ascii")
        return base64.b64encode(base64.b64decode(text_bytes)) == text_bytes
    except Exception:
        return False


def is_hex(text: str) -> bool:
    """Check if a string is valid hexadecimal.

    Note:
        This function does not accept hex strings with '0x' or '0X' prefixes.
        Use int(text, 16) if you need to handle prefixed hex strings.

    Args:
        text: String to check

    Returns:
        True if valid hexadecimal, False otherwise

    Examples:
        >>> is_hex('68656c6c6f')
        True
        >>> is_hex('hello')
        False
        >>> is_hex('123abc')
        True
        >>> is_hex('0x123')  # Prefixed hex strings are rejected
        False
    """
    if not text:
        return False
    # Reject strings with hex prefixes
    if text.startswith(("0x", "0X")):
        return False
    # Check if all characters are valid hex digits
    return all(c in "0123456789abcdefABCDEF" for c in text)


def is_json(text: str) -> bool:
    """Check if a string is valid JSON.

    Args:
        text: String to check

    Returns:
        True if valid JSON, False otherwise

    Examples:
        >>> is_json('{"name": "John"}')
        True
        >>> is_json('[1, 2, 3]')
        True
        >>> is_json('hello')
        False
    """
    if not text:
        return False
    try:
        json.loads(text)
        return True
    except (json.JSONDecodeError, TypeError):
        return False
