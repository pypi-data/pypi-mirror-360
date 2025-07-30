"""Bytes utility functions.

This module provides utility functions for working with bytes and byte strings,
including parsing and formatting byte values with units,
ported from the jsutils library.
"""

import re
from typing import ClassVar


class Bytes:
    """Utility class for working with byte values and formatting."""

    # Byte unit mappings
    UNITS: ClassVar[dict[str, int]] = {
        "b": 1,
        "byte": 1,
        "bytes": 1,
        "kb": 1024,
        "kilobyte": 1024,
        "kilobytes": 1024,
        "mb": 1024**2,
        "megabyte": 1024**2,
        "megabytes": 1024**2,
        "gb": 1024**3,
        "gigabyte": 1024**3,
        "gigabytes": 1024**3,
        "tb": 1024**4,
        "terabyte": 1024**4,
        "terabytes": 1024**4,
        "pb": 1024**5,
        "petabyte": 1024**5,
        "petabytes": 1024**5,
    }

    # Unit abbreviations for formatting
    UNIT_ABBR: ClassVar[list[str]] = ["B", "KB", "MB", "GB", "TB", "PB"]

    @classmethod
    def convert(cls, value: str | int | float) -> int | str:
        """Convert between byte values and formatted strings.

        Args:
            value: Either a byte count (int/float) or a byte string (str)

        Returns:
            If input is numeric, returns formatted string
            If input is string, returns byte count as int

        Examples:
            >>> Bytes.convert(1024)
            '1 KB'
            >>> Bytes.convert('1 KB')
            1024
            >>> Bytes.convert(1536)
            '1.5 KB'
        """
        if isinstance(value, str):
            return cls.parse(value)
        else:
            return cls.format(value)

    @classmethod
    def parse(cls, byte_string: str) -> int:
        """Parse a byte string into a numeric value.

        Args:
            byte_string: String representation of bytes (e.g., '1 KB', '500 MB')

        Returns:
            Number of bytes as integer

        Raises:
            ValueError: If the string format is invalid

        Examples:
            >>> Bytes.parse('1 KB')
            1024
            >>> Bytes.parse('1.5 MB')
            1572864
            >>> Bytes.parse('500')
            500
        """
        if not isinstance(byte_string, str):
            raise ValueError("Input must be a string")

        # Remove extra whitespace and convert to lowercase
        byte_string = byte_string.strip().lower()

        # If it's just a number, return as is
        if byte_string.isdigit():
            return int(byte_string)

        # Try to parse float
        try:
            return int(float(byte_string))
        except ValueError:
            pass

        # Parse with units using regex
        pattern = r"^([0-9]*\.?[0-9]+)\s*([a-z]+)$"
        match = re.match(pattern, byte_string)

        if not match:
            raise ValueError(f"Invalid byte string format: {byte_string}")

        number_str, unit = match.groups()

        try:
            number = float(number_str)
        except ValueError as e:
            raise ValueError(f"Invalid number: {number_str}") from e

        if unit not in cls.UNITS:
            raise ValueError(f"Unknown unit: {unit}")

        return int(number * cls.UNITS[unit])

    @classmethod
    def format(
        cls,
        byte_count: int | float,
        decimals: int = 1,
        thousand_separator: bool = False,
    ) -> str:
        """Format a byte count into a human-readable string.

        Args:
            byte_count: Number of bytes
            decimals: Number of decimal places to show
            thousand_separator: Whether to use thousand separators

        Returns:
            Formatted byte string

        Examples:
            >>> Bytes.format(1024)
            '1 KB'
            >>> Bytes.format(1536, decimals=2)
            '1.50 KB'
            >>> Bytes.format(1234567, thousand_separator=True)
            '1.2 MB'
        """
        if not isinstance(byte_count, int | float):
            raise ValueError("Byte count must be a number")

        if byte_count < 0:
            raise ValueError("Byte count cannot be negative")

        if byte_count == 0:
            return "0 B"

        # Find the appropriate unit
        unit_index = 0
        size = float(byte_count)

        while size >= 1024 and unit_index < len(cls.UNIT_ABBR) - 1:
            size /= 1024
            unit_index += 1

        # Format the number
        if decimals == 0:
            formatted_size = str(round(size))
        else:
            formatted_size = f"{size:.{decimals}f}"
            # Remove trailing zeros after decimal point
            if "." in formatted_size:
                formatted_size = formatted_size.rstrip("0").rstrip(".")

        # Add thousand separator if requested
        if thousand_separator and "." in formatted_size:
            integer_part, decimal_part = formatted_size.split(".")
            integer_part = f"{int(integer_part):,}"
            formatted_size = f"{integer_part}.{decimal_part}"
        elif thousand_separator:
            formatted_size = f"{int(float(formatted_size)):,}"

        return f"{formatted_size} {cls.UNIT_ABBR[unit_index]}"

    @classmethod
    def to_kb(cls, byte_count: int | float) -> float:
        """Convert bytes to kilobytes.

        Args:
            byte_count: Number of bytes

        Returns:
            Number of kilobytes

        Examples:
            >>> Bytes.to_kb(1024)
            1.0
            >>> Bytes.to_kb(1536)
            1.5
        """
        return byte_count / 1024

    @classmethod
    def to_mb(cls, byte_count: int | float) -> float:
        """Convert bytes to megabytes.

        Args:
            byte_count: Number of bytes

        Returns:
            Number of megabytes

        Examples:
            >>> Bytes.to_mb(1048576)
            1.0
            >>> Bytes.to_mb(1572864)
            1.5
        """
        return byte_count / (1024**2)

    @classmethod
    def to_gb(cls, byte_count: int | float) -> float:
        """Convert bytes to gigabytes.

        Args:
            byte_count: Number of bytes

        Returns:
            Number of gigabytes

        Examples:
            >>> Bytes.to_gb(1073741824)
            1.0
            >>> Bytes.to_gb(1610612736)
            1.5
        """
        return byte_count / (1024**3)

    @classmethod
    def to_tb(cls, byte_count: int | float) -> float:
        """Convert bytes to terabytes.

        Args:
            byte_count: Number of bytes

        Returns:
            Number of terabytes

        Examples:
            >>> Bytes.to_tb(1099511627776)
            1.0
        """
        return byte_count / (1024**4)

    @classmethod
    def from_kb(cls, kb_count: int | float) -> int:
        """Convert kilobytes to bytes.

        Args:
            kb_count: Number of kilobytes

        Returns:
            Number of bytes

        Examples:
            >>> Bytes.from_kb(1)
            1024
            >>> Bytes.from_kb(1.5)
            1536
        """
        return int(kb_count * 1024)

    @classmethod
    def from_mb(cls, mb_count: int | float) -> int:
        """Convert megabytes to bytes.

        Args:
            mb_count: Number of megabytes

        Returns:
            Number of bytes

        Examples:
            >>> Bytes.from_mb(1)
            1048576
            >>> Bytes.from_mb(1.5)
            1572864
        """
        return int(mb_count * (1024**2))

    @classmethod
    def from_gb(cls, gb_count: int | float) -> int:
        """Convert gigabytes to bytes.

        Args:
            gb_count: Number of gigabytes

        Returns:
            Number of bytes

        Examples:
            >>> Bytes.from_gb(1)
            1073741824
            >>> Bytes.from_gb(1.5)
            1610612736
        """
        return int(gb_count * (1024**3))

    @classmethod
    def from_tb(cls, tb_count: int | float) -> int:
        """Convert terabytes to bytes.

        Args:
            tb_count: Number of terabytes

        Returns:
            Number of bytes

        Examples:
            >>> Bytes.from_tb(1)
            1099511627776
        """
        return int(tb_count * (1024**4))

    @classmethod
    def compare(cls, value1: str | int | float, value2: str | int | float) -> int:
        """Compare two byte values.

        Args:
            value1: First value (string or numeric)
            value2: Second value (string or numeric)

        Returns:
            -1 if value1 < value2, 0 if equal, 1 if value1 > value2

        Examples:
            >>> Bytes.compare('1 KB', 1024)
            0
            >>> Bytes.compare('1 MB', '1 KB')
            1
            >>> Bytes.compare(512, '1 KB')
            -1
        """
        bytes1 = cls.parse(value1) if isinstance(value1, str) else int(value1)
        bytes2 = cls.parse(value2) if isinstance(value2, str) else int(value2)

        if bytes1 < bytes2:
            return -1
        elif bytes1 > bytes2:
            return 1
        else:
            return 0


# Convenience function that mimics the jsutils API
def bytes_util(value: str | int | float) -> int | str:
    """Convenience function for byte conversion.

    Args:
        value: Either a byte count (int/float) or a byte string (str)

    Returns:
        If input is numeric, returns formatted string
        If input is string, returns byte count as int

    Examples:
        >>> bytes_util(1024)
        '1 KB'
        >>> bytes_util('1 KB')
        1024
        >>> bytes_util(1536)
        '1.5 KB'
    """
    return Bytes.convert(value)


# Additional utility functions
def humanize_bytes(
    byte_count: int | float, decimals: int = 1, binary: bool = True
) -> str:
    """Convert bytes to human readable format.

    Args:
        byte_count: Number of bytes
        decimals: Number of decimal places
        binary: Use binary (1024) or decimal (1000) units

    Returns:
        Human readable byte string

    Examples:
        >>> humanize_bytes(1024)
        '1 KB'
        >>> humanize_bytes(1000, binary=False)
        '1 KB'
        >>> humanize_bytes(1536, decimals=2)
        '1.50 KB'
    """
    if binary:
        return Bytes.format(byte_count, decimals)

    # Decimal units (1000-based)
    units = ["B", "KB", "MB", "GB", "TB", "PB"]
    unit_index = 0
    size = float(byte_count)

    while size >= 1000 and unit_index < len(units) - 1:
        size /= 1000
        unit_index += 1

    if decimals == 0:
        formatted_size = str(round(size))
    else:
        formatted_size = f"{size:.{decimals}f}"
        if "." in formatted_size:
            formatted_size = formatted_size.rstrip("0").rstrip(".")

    return f"{formatted_size} {units[unit_index]}"


def parse_bytes(byte_string: str, binary: bool = True) -> int:
    """Parse byte string to integer.

    Args:
        byte_string: String representation of bytes
        binary: Use binary (1024) or decimal (1000) units

    Returns:
        Number of bytes

    Examples:
        >>> parse_bytes('1 KB')
        1024
        >>> parse_bytes('1 KB', binary=False)
        1000
    """
    if binary:
        return Bytes.parse(byte_string)

    # Handle decimal units
    byte_string = byte_string.strip().lower()

    if byte_string.isdigit():
        return int(byte_string)

    try:
        return int(float(byte_string))
    except ValueError:
        pass

    pattern = r"^([0-9]*\.?[0-9]+)\s*([a-z]+)$"
    match = re.match(pattern, byte_string)

    if not match:
        raise ValueError(f"Invalid byte string format: {byte_string}")

    number_str, unit = match.groups()
    number = float(number_str)

    # Decimal units (1000-based)
    decimal_units = {
        "b": 1,
        "byte": 1,
        "bytes": 1,
        "kb": 1000,
        "kilobyte": 1000,
        "kilobytes": 1000,
        "mb": 1000**2,
        "megabyte": 1000**2,
        "megabytes": 1000**2,
        "gb": 1000**3,
        "gigabyte": 1000**3,
        "gigabytes": 1000**3,
        "tb": 1000**4,
        "terabyte": 1000**4,
        "terabytes": 1000**4,
        "pb": 1000**5,
        "petabyte": 1000**5,
        "petabytes": 1000**5,
    }

    if unit not in decimal_units:
        raise ValueError(f"Unknown unit: {unit}")

    return int(number * decimal_units[unit])


def get_hash(data: str, algorithm: str = "md5") -> str:
    """Generate hash for given data.

    Args:
        data: String data to hash
        algorithm: Hash algorithm to use ('md5', 'sha1', 'sha256'), defaults to 'md5'

    Returns:
        Hexadecimal hash string

    Examples:
        >>> get_hash('hello')
        '5d41402abc4b2a76b9719d911017c592'
        >>> get_hash('hello', 'sha256')
        '2cf24dba4f21d4288094e9b9eb4e5f0164e031c02c90b3a8b26f6c8b'
    """
    import hashlib

    # Convert string to bytes
    data_bytes = data.encode("utf-8")

    # Select hash algorithm
    if algorithm == "md5":
        hasher = hashlib.md5(usedforsecurity=False)
    elif algorithm == "sha1":
        hasher = hashlib.sha1(usedforsecurity=False)
    elif algorithm == "sha256":
        hasher = hashlib.sha256()
    else:
        raise ValueError(f"Unsupported hash algorithm: {algorithm}")

    hasher.update(data_bytes)
    return hasher.hexdigest()


def to_base64(data: str) -> str:
    """Encode string data to base64.

    Args:
        data: String data to encode

    Returns:
        Base64 encoded string

    Examples:
        >>> to_base64('hello')
        'aGVsbG8='
        >>> to_base64('world')
        'd29ybGQ='
    """
    import base64

    # Convert string to bytes
    data_bytes = data.encode("utf-8")

    # Encode to base64
    encoded_bytes = base64.b64encode(data_bytes)

    # Convert back to string
    return encoded_bytes.decode("utf-8")


def from_base64(data: str) -> str:
    """Decode base64 string data.

    Args:
        data: Base64 encoded string

    Returns:
        Decoded string

    Examples:
        >>> from_base64('aGVsbG8=')
        'hello'
        >>> from_base64('d29ybGQ=')
        'world'
    """
    import base64

    # Convert string to bytes
    data_bytes = data.encode("utf-8")

    # Decode from base64
    decoded_bytes = base64.b64decode(data_bytes)

    # Convert back to string
    return decoded_bytes.decode("utf-8")
