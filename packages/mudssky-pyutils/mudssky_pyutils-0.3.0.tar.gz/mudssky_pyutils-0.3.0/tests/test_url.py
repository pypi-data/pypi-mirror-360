"""Tests for URL utility functions."""

import pytest

from pyutils.url import (
    URLParser,
    build_url,
    decode_uri,
    decode_uri_component,
    encode_uri,
    encode_uri_component,
    get_domain,
    get_query_params,
    is_valid_url,
    parse_url,
)


class TestURLParser:
    """Test URLParser class."""

    def test_parse_complete_url(self):
        """Test parsing a complete URL."""
        url = "https://user:pass@example.com:8080/path/to/page?query=value&foo=bar#section"
        parser = URLParser(url)

        assert parser.href == url
        assert parser.protocol == "https:"
        assert parser.hostname == "example.com"
        assert parser.port == "8080"
        assert parser.pathname == "/path/to/page"
        assert parser.search == "?query=value&foo=bar"
        assert parser.hash == "#section"
        assert parser.origin == "https://example.com:8080"
        assert parser.username == "user"
        assert parser.password == "pass"  # noqa: S105

        query_params = parser.get_query_params()
        assert query_params == {"query": "value", "foo": "bar"}

    def test_parse_simple_url(self):
        """Test parsing a simple URL."""
        url = "https://example.com/path"
        parser = URLParser(url)

        assert parser.href == url
        assert parser.protocol == "https:"
        assert parser.hostname == "example.com"
        assert parser.port == ""
        assert parser.pathname == "/path"
        assert parser.search == ""
        assert parser.hash == ""
        assert parser.origin == "https://example.com"
        assert parser.username == ""
        assert parser.password == ""

    def test_parse_url_with_default_port(self):
        """Test parsing URL with default ports."""
        # HTTP default port
        parser = URLParser("http://example.com/path")
        assert parser.port == ""
        assert parser.origin == "http://example.com"

        # HTTPS default port
        parser = URLParser("https://example.com/path")
        assert parser.port == ""
        assert parser.origin == "https://example.com"

    def test_parse_url_with_query_only(self):
        """Test parsing URL with query parameters only."""
        url = "https://example.com?foo=bar&baz=qux"
        parser = URLParser(url)

        assert parser.pathname == "/"
        assert parser.search == "?foo=bar&baz=qux"
        query_params = parser.get_query_params()
        assert query_params == {"foo": "bar", "baz": "qux"}

    def test_parse_invalid_url(self):
        """Test parsing invalid URL."""
        with pytest.raises(ValueError, match="Invalid URL"):
            URLParser("not-a-url")

        with pytest.raises(ValueError, match="Invalid URL"):
            URLParser("")


class TestURLFunctions:
    """Test URL utility functions."""

    def test_parse_url(self):
        """Test parse_url function."""
        url = "https://example.com:8080/path?query=value#section"
        result = parse_url(url)

        expected = {
            "href": url,
            "protocol": "https:",
            "hostname": "example.com",
            "port": "8080",
            "pathname": "/path",
            "search": "?query=value",
            "hash": "#section",
            "origin": "https://example.com:8080",
            "username": "",
            "password": "",
        }

        assert result == expected

    def test_encode_uri_component(self):
        """Test encode_uri_component function."""
        # Test special characters
        assert encode_uri_component("hello world") == "hello%20world"
        assert encode_uri_component("hello@world.com") == "hello%40world.com"
        assert encode_uri_component("hello/world") == "hello%2Fworld"
        assert encode_uri_component("hello?world=test") == "hello%3Fworld%3Dtest"

        # Test already encoded
        assert encode_uri_component("hello%20world") == "hello%2520world"

        # Test empty string
        assert encode_uri_component("") == ""

    def test_decode_uri_component(self):
        """Test decode_uri_component function."""
        # Test encoded characters
        assert decode_uri_component("hello%20world") == "hello world"
        assert decode_uri_component("hello%40world.com") == "hello@world.com"
        assert decode_uri_component("hello%2Fworld") == "hello/world"
        assert decode_uri_component("hello%3Fworld%3Dtest") == "hello?world=test"

        # Test unencoded string
        assert decode_uri_component("hello world") == "hello world"

        # Test empty string
        assert decode_uri_component("") == ""

        # Test invalid encoding
        with pytest.raises(ValueError):
            decode_uri_component("hello%ZZ")

    def test_encode_uri(self):
        """Test encode_uri function."""
        # Test URI with special characters
        uri = "https://example.com/path with spaces?query=hello world"
        encoded = encode_uri(uri)
        assert "hello%20world" in encoded
        assert "path%20with%20spaces" in encoded

        # Test URI components are preserved
        assert "https://" in encoded
        assert "example.com" in encoded
        assert "?" in encoded
        assert "=" in encoded

    def test_decode_uri(self):
        """Test decode_uri function."""
        # Test encoded URI
        encoded_uri = "https://example.com/path%20with%20spaces?query=hello%20world"
        decoded = decode_uri(encoded_uri)
        assert decoded == "https://example.com/path with spaces?query=hello world"

        # Test unencoded URI
        uri = "https://example.com/path"
        assert decode_uri(uri) == uri

    def test_build_url(self):
        """Test build_url function."""
        # Test with all components
        result = build_url(
            protocol="https",
            hostname="example.com",
            port=8080,
            pathname="/path/to/page",
            query_params={"foo": "bar", "baz": "qux"},
            hash_fragment="section",
        )
        expected = "https://example.com:8080/path/to/page?foo=bar&baz=qux#section"
        assert result == expected

        # Test with minimal components
        result = build_url(hostname="example.com")
        assert result == "http://example.com"

        # Test with custom protocol
        result = build_url(protocol="ftp", hostname="files.example.com")
        assert result == "ftp://files.example.com"

        # Test with query params only
        result = build_url(hostname="example.com", query_params={"search": "python"})
        assert result == "http://example.com?search=python"

    def test_is_valid_url(self):
        """Test is_valid_url function."""
        # Valid URLs
        assert is_valid_url("https://example.com") is True
        assert is_valid_url("http://example.com/path") is True
        assert is_valid_url("ftp://files.example.com") is True
        assert is_valid_url("https://example.com:8080/path?query=value#section") is True

        # Invalid URLs
        assert is_valid_url("not-a-url") is False
        assert is_valid_url("") is False
        assert is_valid_url("example.com") is False  # Missing protocol
        assert is_valid_url("https://") is False  # Missing hostname
        assert is_valid_url("://example.com") is False  # Missing protocol

    def test_get_domain(self):
        """Test get_domain function."""
        # Test various URLs
        assert get_domain("https://example.com/path") == "example.com"
        assert get_domain("http://subdomain.example.com") == "subdomain.example.com"
        assert get_domain("https://example.com:8080/path") == "example.com"
        assert get_domain("ftp://files.example.org") == "files.example.org"

        # Test invalid URLs
        assert get_domain("not-a-url") is None
        assert get_domain("") is None

    def test_get_query_params(self):
        """Test get_query_params function."""
        # Test URL with query parameters
        url = "https://example.com/path?foo=bar&baz=qux&empty="
        params = get_query_params(url)
        assert params == {"foo": "bar", "baz": "qux", "empty": ""}

        # Test URL without query parameters
        url = "https://example.com/path"
        params = get_query_params(url)
        assert params == {}

        # Test URL with encoded query parameters
        url = "https://example.com/path?name=John%20Doe&email=john%40example.com"
        params = get_query_params(url)
        assert params == {"name": "John Doe", "email": "john@example.com"}

        # Test URL with duplicate parameters (last one wins)
        url = "https://example.com/path?foo=bar&foo=baz"
        params = get_query_params(url)
        assert params == {"foo": "baz"}

        # Test invalid URL
        params = get_query_params("not-a-url")
        assert params == {}

    def test_edge_cases(self):
        """Test edge cases."""
        # Test URL with only hash
        parser = URLParser("https://example.com#section")
        assert parser.pathname == "/"
        assert parser.search == ""
        assert parser.hash == "#section"

        # Test URL with empty query parameter
        parser = URLParser("https://example.com?foo=")
        params = parser.get_query_params()
        assert params == {"foo": ""}

        # Test URL with special characters in path
        parser = URLParser("https://example.com/path%20with%20spaces")
        assert parser.pathname == "/path%20with%20spaces"

        # Test localhost URLs
        parser = URLParser("http://localhost:3000/app")
        assert parser.hostname == "localhost"
        assert parser.port == "3000"
        assert parser.origin == "http://localhost:3000"
