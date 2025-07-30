"""URL utility functions.

This module provides utility functions for working with URLs,
porting JavaScript URL object methods and other URL utilities to Python.
"""

import urllib.parse


class URLParser:
    """URL parser class similar to JavaScript URL object.

    Provides methods to parse and manipulate URLs similar to the JavaScript URL API.
    """

    def __init__(self, url: str, base: str | None = None):
        """Initialize URL parser.

        Args:
            url: URL string to parse
            base: Base URL for relative URLs

        Examples:
            >>> parser = URLParser('https://example.com/path?query=value#hash')
            >>> parser.hostname
            'example.com'
        """
        if not url:
            raise ValueError("Invalid URL: empty string")

        if base and not urllib.parse.urlparse(url).scheme:
            url = urllib.parse.urljoin(base, url)

        self._parsed = urllib.parse.urlparse(url)

        # Validate that we have at least a scheme
        if not self._parsed.scheme:
            raise ValueError("Invalid URL: missing scheme")

        self._query_params = urllib.parse.parse_qs(self._parsed.query)

    @property
    def href(self) -> str:
        """Get the complete URL.

        Returns:
            Complete URL string
        """
        return self._parsed.geturl()

    @property
    def protocol(self) -> str:
        """Get the protocol (scheme) of the URL.

        Returns:
            Protocol string (e.g., 'https:')
        """
        return f"{self._parsed.scheme}:" if self._parsed.scheme else ""

    @property
    def hostname(self) -> str:
        """Get the hostname of the URL.

        Returns:
            Hostname string
        """
        return self._parsed.hostname or ""

    @property
    def port(self) -> str:
        """Get the port of the URL.

        Returns:
            Port string (empty if default port)
        """
        return str(self._parsed.port) if self._parsed.port else ""

    @property
    def pathname(self) -> str:
        """Get the pathname of the URL.

        Returns:
            Pathname string (defaults to '/' if empty)
        """
        return self._parsed.path or "/"

    @property
    def search(self) -> str:
        """Get the search (query) string of the URL.

        Returns:
            Search string including '?' prefix
        """
        return f"?{self._parsed.query}" if self._parsed.query else ""

    @property
    def hash(self) -> str:
        """Get the hash (fragment) of the URL.

        Returns:
            Hash string including '#' prefix
        """
        return f"#{self._parsed.fragment}" if self._parsed.fragment else ""

    @property
    def origin(self) -> str:
        """Get the origin of the URL.

        Returns:
            Origin string (protocol + hostname + port)
        """
        if not self._parsed.scheme or not self._parsed.hostname:
            return ""
        origin = f"{self._parsed.scheme}://{self._parsed.hostname}"
        if self._parsed.port:
            origin += f":{self._parsed.port}"
        return origin

    @property
    def username(self) -> str:
        """Get the username from the URL.

        Returns:
            Username string
        """
        return self._parsed.username or ""

    @property
    def password(self) -> str:
        """Get the password from the URL.

        Returns:
            Password string
        """
        return self._parsed.password or ""

    def get_query_params(self) -> dict[str, str]:
        """Get query parameters as a dictionary.

        Returns:
            Dictionary of query parameters

        Examples:
            >>> parser = URLParser('https://example.com?name=John&age=30')
            >>> params = parser.get_query_params()
            >>> params['name']
            'John'
        """
        if not self._parsed.query:
            return {}
        return dict(urllib.parse.parse_qsl(self._parsed.query, keep_blank_values=True))


def parse_url(url: str, base: str | None = None) -> dict[str, str]:
    """Parse a URL string into a dictionary.

    Args:
        url: URL string to parse
        base: Base URL for relative URLs

    Returns:
        Dictionary with URL components

    Examples:
        >>> result = parse_url('https://example.com/path')
        >>> result['hostname']
        'example.com'
    """
    parser = URLParser(url, base)
    return {
        "href": parser.href,
        "protocol": parser.protocol,
        "hostname": parser.hostname,
        "port": parser.port,
        "pathname": parser.pathname,
        "search": parser.search,
        "hash": parser.hash,
        "origin": parser.origin,
        "username": parser.username,
        "password": parser.password,
    }


def encode_uri_component(text: str) -> str:
    """Encode a string for use in a URI component (like JavaScript encodeURIComponent).

    Args:
        text: String to encode

    Returns:
        Encoded string

    Examples:
        >>> encode_uri_component('hello world')
        'hello%20world'
        >>> encode_uri_component('user@example.com')
        'user%40example.com'
    """
    return urllib.parse.quote(text, safe="")


def decode_uri_component(text: str) -> str:
    """Decode a URI component string (like JavaScript decodeURIComponent).

    Args:
        text: String to decode

    Returns:
        Decoded string

    Raises:
        ValueError: If the string contains invalid percent encoding

    Examples:
        >>> decode_uri_component('hello%20world')
        'hello world'
        >>> decode_uri_component('user%40example.com')
        'user@example.com'
    """
    import re

    # Check for invalid percent encoding patterns
    if re.search(r"%[^0-9A-Fa-f]", text) or re.search(
        r"%[0-9A-Fa-f][^0-9A-Fa-f]", text
    ):
        raise ValueError("Invalid percent encoding")

    try:
        return urllib.parse.unquote(text, errors="strict")
    except UnicodeDecodeError as e:
        raise ValueError(f"Invalid percent encoding: {e}") from e


def encode_uri(uri: str) -> str:
    """Encode a complete URI (like JavaScript encodeURI).

    Args:
        uri: URI to encode

    Returns:
        Encoded URI

    Examples:
        >>> encode_uri('https://example.com/path with spaces')
        'https://example.com/path%20with%20spaces'
    """
    return urllib.parse.quote(uri, safe=":/?#[]@!$&'()*+,;=")


def decode_uri(uri: str) -> str:
    """Decode a complete URI (like JavaScript decodeURI).

    Args:
        uri: URI to decode

    Returns:
        Decoded URI

    Examples:
        >>> decode_uri('https://example.com/path%20with%20spaces')
        'https://example.com/path with spaces'
    """
    return urllib.parse.unquote(uri)


def build_url(
    protocol: str = "http",
    hostname: str = "",
    port: int | None = None,
    pathname: str = "",
    query_params: dict[str, str] | None = None,
    hash_fragment: str = "",
) -> str:
    """Build a URL from components.

    Args:
        protocol: Protocol (without colon)
        hostname: Hostname
        port: Port number
        pathname: Path
        query_params: Query parameters
        hash_fragment: Hash fragment

    Returns:
        Complete URL string

    Examples:
        >>> build_url(
        ...     hostname='example.com',
        ...     pathname='/api/users',
        ...     query_params={'page': '1'}
        ... )
        'http://example.com/api/users?page=1'
    """
    if not hostname:
        raise ValueError("hostname is required")

    # Build base URL
    url = f"{protocol}://{hostname}"

    # Add port if specified and not default
    if port and not (
        (protocol == "http" and port == 80) or (protocol == "https" and port == 443)
    ):
        url += f":{port}"

    # Add pathname
    if pathname:
        if not pathname.startswith("/"):
            pathname = "/" + pathname
        url += pathname

    # Add query parameters
    if query_params:
        query_string = urllib.parse.urlencode(query_params)
        url += "?" + query_string

    # Add hash fragment
    if hash_fragment:
        if not hash_fragment.startswith("#"):
            hash_fragment = "#" + hash_fragment
        url += hash_fragment

    return url


def is_valid_url(url: str) -> bool:
    """Check if a string is a valid URL.

    Args:
        url: String to check

    Returns:
        True if valid URL, False otherwise

    Examples:
        >>> is_valid_url('https://example.com')
        True
        >>> is_valid_url('not-a-url')
        False
        >>> is_valid_url('ftp://files.example.com')
        True
    """
    try:
        result = urllib.parse.urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def get_domain(url: str) -> str | None:
    """Extract domain from URL.

    Args:
        url: URL string

    Returns:
        Domain string or None if invalid

    Examples:
        >>> get_domain('https://www.example.com/path')
        'www.example.com'
        >>> get_domain('http://subdomain.example.org:8080/api')
        'subdomain.example.org'
        >>> get_domain('invalid-url')
        None
    """
    try:
        parsed = urllib.parse.urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return None
        return parsed.hostname
    except Exception:
        return None


def get_query_params(url: str) -> dict[str, str]:
    """Extract query parameters from URL.

    Args:
        url: URL string

    Returns:
        Dictionary of query parameters

    Examples:
        >>> get_query_params(
        ...     'https://example.com/path?foo=bar&baz=qux'
        ... )
        {'foo': 'bar', 'baz': 'qux'}
        >>> get_query_params('https://example.com/path')
        {}
    """
    try:
        parsed = urllib.parse.urlparse(url)
        if not parsed.query:
            return {}
        return dict(urllib.parse.parse_qsl(parsed.query, keep_blank_values=True))
    except Exception:
        return {}
