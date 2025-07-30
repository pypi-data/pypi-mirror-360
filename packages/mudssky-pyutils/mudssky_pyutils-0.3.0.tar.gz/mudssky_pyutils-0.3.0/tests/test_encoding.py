"""Tests for encoding utility functions."""

import base64
import json
import re
from urllib.parse import quote

import pytest

from pyutils.encoding import (
    atob,
    btoa,
    decode_base64,
    decode_hex,
    encode_base64,
    encode_hex,
    escape_html,
    escape_regex,
    generate_random_string,
    hash_string,
    is_base64,
    is_hex,
    is_json,
    json_parse,
    json_stringify,
    unescape_html,
    url_decode,
    url_encode,
)


class TestBase64Encoding:
    """Test Base64 encoding functions."""

    def test_btoa(self):
        """Test btoa function."""
        # Basic encoding
        assert btoa("hello") == base64.b64encode(b"hello").decode()
        assert btoa("Hello, World!") == base64.b64encode(b"Hello, World!").decode()

        # Empty string
        assert btoa("") == ""

        # Special characters
        assert btoa("Hello 世界") == base64.b64encode("Hello 世界".encode()).decode()

    def test_atob(self):
        """Test atob function."""
        # Basic decoding
        encoded = btoa("hello")
        assert atob(encoded) == "hello"

        encoded = btoa("Hello, World!")
        assert atob(encoded) == "Hello, World!"

        # Empty string
        assert atob("") == ""

        # Special characters
        encoded = btoa("Hello 世界")
        assert atob(encoded) == "Hello 世界"

        # Invalid base64
        with pytest.raises(ValueError):
            atob("invalid base64!")

    def test_encode_decode_base64(self):
        """Test encode_base64 and decode_base64 functions."""
        # Test round trip
        original = "Hello, World! 你好世界"
        encoded = encode_base64(original)
        decoded = decode_base64(encoded)
        assert decoded == original

        # Test empty string
        assert encode_base64("") == ""
        assert decode_base64("") == ""

        # Test binary data
        binary_data = b"\x00\x01\x02\x03\xff"
        encoded = base64.b64encode(binary_data).decode()
        decoded_bytes = base64.b64decode(encoded)
        assert decoded_bytes == binary_data


class TestHTMLEncoding:
    """Test HTML encoding functions."""

    def test_escape_html(self):
        """Test escape_html function."""
        # Basic HTML entities
        assert (
            escape_html("<div>Hello & goodbye</div>")
            == "&lt;div&gt;Hello &amp; goodbye&lt;/div&gt;"
        )
        assert (
            escape_html("Say \"hello\" to 'world'")
            == "Say &quot;hello&quot; to &#x27;world&#x27;"
        )

        # Empty string
        assert escape_html("") == ""

        # No special characters
        assert escape_html("Hello World") == "Hello World"

        # All special characters
        assert escape_html("<>&\"'") == "&lt;&gt;&amp;&quot;&#x27;"

    def test_unescape_html(self):
        """Test unescape_html function."""
        # Basic HTML entities
        assert (
            unescape_html("&lt;div&gt;Hello &amp; goodbye&lt;/div&gt;")
            == "<div>Hello & goodbye</div>"
        )
        assert (
            unescape_html("Say &quot;hello&quot; to &#x27;world&#x27;")
            == "Say \"hello\" to 'world'"
        )

        # Empty string
        assert unescape_html("") == ""

        # No entities
        assert unescape_html("Hello World") == "Hello World"

        # Round trip
        original = '<div class="test">Hello & "world"</div>'
        escaped = escape_html(original)
        unescaped = unescape_html(escaped)
        assert unescaped == original


class TestHexEncoding:
    """Test hexadecimal encoding functions."""

    def test_encode_hex(self):
        """Test encode_hex function."""
        # Basic encoding
        assert encode_hex("hello") == b"hello".hex()
        assert encode_hex("Hello, World!") == b"Hello, World!".hex()

        # Empty string
        assert encode_hex("") == ""

        # Special characters
        result = encode_hex("Hello 世界")
        expected = "Hello 世界".encode().hex()
        assert result == expected

    def test_decode_hex(self):
        """Test decode_hex function."""
        # Basic decoding
        hex_str = encode_hex("hello")
        assert decode_hex(hex_str) == "hello"

        # Empty string
        assert decode_hex("") == ""

        # Round trip
        original = "Hello, World! 你好"
        encoded = encode_hex(original)
        decoded = decode_hex(encoded)
        assert decoded == original

        # Invalid hex
        with pytest.raises(ValueError):
            decode_hex("invalid hex string")

        with pytest.raises(ValueError):
            decode_hex("zz")  # Invalid hex characters


class TestJSONFunctions:
    """Test JSON utility functions."""

    def test_json_stringify(self):
        """Test json_stringify function."""
        # Basic objects
        assert json_stringify({"key": "value"}) == '{"key": "value"}'
        assert json_stringify([1, 2, 3]) == "[1, 2, 3]"
        assert json_stringify("hello") == '"hello"'
        assert json_stringify(123) == "123"
        assert json_stringify(True) == "true"
        assert json_stringify(None) == "null"

        # Complex object
        obj = {
            "name": "John",
            "age": 30,
            "active": True,
            "scores": [85, 90, 78],
            "address": None,
        }
        result = json_stringify(obj)
        # Parse it back to verify it's valid JSON
        parsed = json.loads(result)
        assert parsed == obj

    def test_json_parse(self):
        """Test json_parse function."""
        # Basic parsing
        assert json_parse('{"key": "value"}') == {"key": "value"}
        assert json_parse("[1, 2, 3]") == [1, 2, 3]
        assert json_parse('"hello"') == "hello"
        assert json_parse("123") == 123
        assert json_parse("true") is True
        assert json_parse("null") is None

        # Invalid JSON
        with pytest.raises(ValueError):
            json_parse("invalid json")

        with pytest.raises(ValueError):
            json_parse("{key: 'value'}")  # Missing quotes

        # Round trip
        original = {"name": "Alice", "scores": [95, 87, 92], "active": True}
        stringified = json_stringify(original)
        parsed = json_parse(stringified)
        assert parsed == original


class TestURLEncoding:
    """Test URL encoding functions."""

    def test_url_encode(self):
        """Test url_encode function."""
        # Basic encoding
        assert url_encode("hello world") == quote("hello world")
        assert url_encode("hello@world.com") == quote("hello@world.com")

        # Special characters
        assert url_encode("hello/world?test=1") == quote("hello/world?test=1")

        # Empty string
        assert url_encode("") == ""

        # Unicode characters
        assert url_encode("你好世界") == quote("你好世界")

    def test_url_decode(self):
        """Test url_decode function."""
        # Basic decoding
        encoded = url_encode("hello world")
        assert url_decode(encoded) == "hello world"

        # Special characters
        encoded = url_encode("hello@world.com")
        assert url_decode(encoded) == "hello@world.com"

        # Empty string
        assert url_decode("") == ""

        # Round trip
        original = "Hello, World! 你好世界 @#$%"
        encoded = url_encode(original)
        decoded = url_decode(encoded)
        assert decoded == original


class TestUtilityFunctions:
    """Test utility functions."""

    def test_escape_regex(self):
        """Test escape_regex function."""
        # Special regex characters
        assert escape_regex("hello.world") == "hello\\.world"
        assert escape_regex("test[123]") == "test\\[123\\]"
        assert escape_regex("a+b*c?") == "a\\+b\\*c\\?"
        assert escape_regex("(group)") == "\\(group\\)"

        # No special characters
        assert escape_regex("hello") == "hello"

        # Empty string
        assert escape_regex("") == ""

        # Test that escaped string works in regex
        pattern = "hello.world"
        escaped = escape_regex(pattern)
        regex = re.compile(escaped)
        assert regex.search("hello.world") is not None
        assert regex.search("helloxworld") is None

    def test_hash_string(self):
        """Test hash_string function."""
        # Basic hashing
        hash1 = hash_string("hello")
        hash2 = hash_string("hello")
        assert hash1 == hash2  # Same input should produce same hash

        # Different inputs should produce different hashes
        hash3 = hash_string("world")
        assert hash1 != hash3

        # Hash should be hexadecimal string
        assert all(c in "0123456789abcdef" for c in hash1)

        # Hash should be 64 characters (SHA-256)
        assert len(hash1) == 64

        # Test with different algorithms
        md5_hash = hash_string("hello", "md5")
        assert len(md5_hash) == 32

        sha1_hash = hash_string("hello", "sha1")
        assert len(sha1_hash) == 40

        # Invalid algorithm
        with pytest.raises(ValueError):
            hash_string("hello", "invalid")

    def test_generate_random_string(self):
        """Test generate_random_string function."""
        # Default length
        random_str = generate_random_string()
        assert len(random_str) == 16
        assert all(
            c in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
            for c in random_str
        )

        # Custom length
        random_str = generate_random_string(32)
        assert len(random_str) == 32

        # Custom characters
        random_str = generate_random_string(10, "abc123")
        assert len(random_str) == 10
        assert all(c in "abc123" for c in random_str)

        # Two calls should produce different strings
        str1 = generate_random_string()
        str2 = generate_random_string()
        assert str1 != str2

        # Zero length
        assert generate_random_string(0) == ""


class TestValidationFunctions:
    """Test validation functions."""

    def test_is_base64(self):
        """Test is_base64 function."""
        # Valid base64
        assert is_base64(btoa("hello")) is True
        assert is_base64("SGVsbG8gV29ybGQ=") is True  # "Hello World"
        assert is_base64("YWJjZA==") is True  # "abcd"

        # Invalid base64
        assert is_base64("invalid base64!") is False
        assert is_base64("SGVsbG8gV29ybGQ") is False  # Missing padding
        assert is_base64("") is False
        assert is_base64("123") is False

    def test_is_hex(self):
        """Test is_hex function."""
        # Valid hex
        assert is_hex("deadbeef") is True
        assert is_hex("123456789abcdef") is True
        assert is_hex("DEADBEEF") is True
        assert is_hex("0123456789ABCDEF") is True

        # Invalid hex
        assert is_hex("hello") is False
        assert is_hex("123g") is False  # 'g' is not hex
        assert is_hex("") is False
        assert is_hex("0x123") is False  # Has prefix

    def test_is_json(self):
        """Test is_json function."""
        # Valid JSON
        assert is_json('{"key": "value"}') is True
        assert is_json("[1, 2, 3]") is True
        assert is_json('"hello"') is True
        assert is_json("123") is True
        assert is_json("true") is True
        assert is_json("null") is True

        # Invalid JSON
        assert is_json("invalid json") is False
        assert is_json("{key: 'value'}") is False  # Missing quotes
        assert is_json("{'key': 'value'}") is False  # Single quotes
        assert is_json("") is False
        assert is_json("undefined") is False

    def test_edge_cases(self):
        """Test edge cases."""
        # Empty inputs
        assert btoa("") == ""
        assert atob("") == ""
        assert encode_hex("") == ""
        assert decode_hex("") == ""
        assert url_encode("") == ""
        assert url_decode("") == ""
        assert escape_html("") == ""
        assert unescape_html("") == ""
        assert escape_regex("") == ""

        # Unicode handling
        unicode_text = "Hello 世界 🌍 émojis"

        # Base64 round trip with unicode
        encoded = btoa(unicode_text)
        decoded = atob(encoded)
        assert decoded == unicode_text

        # Hex round trip with unicode
        hex_encoded = encode_hex(unicode_text)
        hex_decoded = decode_hex(hex_encoded)
        assert hex_decoded == unicode_text

        # URL encoding with unicode
        url_encoded = url_encode(unicode_text)
        url_decoded = url_decode(url_encoded)
        assert url_decoded == unicode_text
