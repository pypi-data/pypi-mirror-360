#!/usr/bin/env python

"""Tests for bytes module."""

import pytest

from pyutils.bytes import Bytes, bytes_util, humanize_bytes, parse_bytes


class TestBytes:
    """Test Bytes utility class."""

    def test_convert_numeric_to_string(self):
        """Test converting numeric values to formatted strings."""
        assert Bytes.convert(1024) == "1 KB"
        assert Bytes.convert(1536) == "1.5 KB"
        assert Bytes.convert(1048576) == "1 MB"
        assert Bytes.convert(0) == "0 B"

    def test_convert_string_to_numeric(self):
        """Test converting formatted strings to numeric values."""
        assert Bytes.convert("1 KB") == 1024
        assert Bytes.convert("1.5 KB") == 1536
        assert Bytes.convert("1 MB") == 1048576
        assert Bytes.convert("500") == 500

    def test_parse_basic(self):
        """Test basic parsing functionality."""
        assert Bytes.parse("1 KB") == 1024
        assert Bytes.parse("1.5 MB") == 1572864
        assert Bytes.parse("500") == 500
        assert Bytes.parse("2 GB") == 2147483648

    def test_parse_case_insensitive(self):
        """Test case insensitive parsing."""
        assert Bytes.parse("1 kb") == 1024
        assert Bytes.parse("1 KB") == 1024
        assert Bytes.parse("1 Kb") == 1024
        assert Bytes.parse("1 kB") == 1024

    def test_parse_with_spaces(self):
        """Test parsing with various spacing."""
        assert Bytes.parse("1KB") == 1024
        assert Bytes.parse("1 KB") == 1024
        assert Bytes.parse("  1   KB  ") == 1024

    def test_parse_invalid_format(self):
        """Test parsing with invalid formats."""
        with pytest.raises(ValueError):
            Bytes.parse("invalid")

        with pytest.raises(ValueError):
            Bytes.parse("1 XB")  # Invalid unit

        with pytest.raises(ValueError):
            Bytes.parse("abc KB")  # Invalid number

    def test_parse_non_string_input(self):
        """Test parsing with non-string input."""
        with pytest.raises(ValueError):
            Bytes.parse(1024)

    def test_format_basic(self):
        """Test basic formatting functionality."""
        assert Bytes.format(1024) == "1 KB"
        assert Bytes.format(1536) == "1.5 KB"
        assert Bytes.format(1048576) == "1 MB"
        assert Bytes.format(0) == "0 B"

    def test_format_with_decimals(self):
        """Test formatting with different decimal places."""
        assert Bytes.format(1536, decimals=0) == "2 KB"
        assert Bytes.format(1536, decimals=1) == "1.5 KB"
        assert Bytes.format(1536, decimals=2) == "1.5 KB"  # Trailing zeros are removed

    def test_format_with_thousand_separator(self):
        """Test formatting with thousand separators."""
        result = Bytes.format(1234567, thousand_separator=True)
        assert "1.2 MB" in result or "1,234,567" in result

    def test_format_invalid_input(self):
        """Test formatting with invalid input."""
        with pytest.raises(ValueError):
            Bytes.format("invalid")

        with pytest.raises(ValueError):
            Bytes.format(-1024)  # Negative value

    def test_unit_conversions_to(self):
        """Test conversion to various units."""
        assert Bytes.to_kb(1024) == 1.0
        assert Bytes.to_kb(1536) == 1.5

        assert Bytes.to_mb(1048576) == 1.0
        assert Bytes.to_mb(1572864) == 1.5

        assert Bytes.to_gb(1073741824) == 1.0
        assert Bytes.to_gb(1610612736) == 1.5

        assert Bytes.to_tb(1099511627776) == 1.0

    def test_unit_conversions_from(self):
        """Test conversion from various units."""
        assert Bytes.from_kb(1) == 1024
        assert Bytes.from_kb(1.5) == 1536

        assert Bytes.from_mb(1) == 1048576
        assert Bytes.from_mb(1.5) == 1572864

        assert Bytes.from_gb(1) == 1073741824
        assert Bytes.from_gb(1.5) == 1610612736

        assert Bytes.from_tb(1) == 1099511627776

    def test_compare(self):
        """Test comparison functionality."""
        assert Bytes.compare("1 KB", 1024) == 0
        assert Bytes.compare("1 MB", "1 KB") == 1
        assert Bytes.compare(512, "1 KB") == -1
        assert Bytes.compare("2 KB", "1 KB") == 1
        assert Bytes.compare("1 KB", "2 KB") == -1


class TestBytesUtil:
    """Test bytes_util convenience function."""

    def test_bytes_util_numeric_input(self):
        """Test bytes_util with numeric input."""
        assert bytes_util(1024) == "1 KB"
        assert bytes_util(1536) == "1.5 KB"
        assert bytes_util(0) == "0 B"

    def test_bytes_util_string_input(self):
        """Test bytes_util with string input."""
        assert bytes_util("1 KB") == 1024
        assert bytes_util("1.5 KB") == 1536
        assert bytes_util("500") == 500

    def test_bytes_util_roundtrip(self):
        """Test bytes_util roundtrip conversion."""
        original = 1536
        formatted = bytes_util(original)
        parsed = bytes_util(formatted)
        assert parsed == original


class TestHumanizeBytes:
    """Test humanize_bytes function."""

    def test_humanize_bytes_binary(self):
        """Test humanize_bytes with binary units (default)."""
        assert humanize_bytes(1024) == "1 KB"
        assert humanize_bytes(1536) == "1.5 KB"
        assert humanize_bytes(1048576) == "1 MB"

    def test_humanize_bytes_decimal(self):
        """Test humanize_bytes with decimal units."""
        assert humanize_bytes(1000, binary=False) == "1 KB"
        assert humanize_bytes(1500, binary=False) == "1.5 KB"
        assert humanize_bytes(1000000, binary=False) == "1 MB"

    def test_humanize_bytes_decimals(self):
        """Test humanize_bytes with different decimal places."""
        assert humanize_bytes(1536, decimals=0) == "2 KB"
        assert humanize_bytes(1536, decimals=1) == "1.5 KB"
        assert (
            humanize_bytes(1536, decimals=2) == "1.5 KB"
        )  # Trailing zeros are removed


class TestParseBytes:
    """Test parse_bytes function."""

    def test_parse_bytes_binary(self):
        """Test parse_bytes with binary units (default)."""
        assert parse_bytes("1 KB") == 1024
        assert parse_bytes("1.5 KB") == 1536
        assert parse_bytes("1 MB") == 1048576

    def test_parse_bytes_decimal(self):
        """Test parse_bytes with decimal units."""
        assert parse_bytes("1 KB", binary=False) == 1000
        assert parse_bytes("1.5 KB", binary=False) == 1500
        assert parse_bytes("1 MB", binary=False) == 1000000

    def test_parse_bytes_plain_numbers(self):
        """Test parse_bytes with plain numbers."""
        assert parse_bytes("1024") == 1024
        assert parse_bytes("500") == 500
        assert parse_bytes("1024.5") == 1024

    def test_parse_bytes_invalid(self):
        """Test parse_bytes with invalid input."""
        with pytest.raises(ValueError):
            parse_bytes("invalid")

        with pytest.raises(ValueError):
            parse_bytes("1 XB")  # Invalid unit


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_zero_bytes(self):
        """Test handling of zero bytes."""
        assert Bytes.format(0) == "0 B"
        assert Bytes.convert(0) == "0 B"
        assert humanize_bytes(0) == "0 B"

    def test_very_large_numbers(self):
        """Test handling of very large numbers."""
        # Test petabytes
        pb_value = 1024**5
        assert "PB" in Bytes.format(pb_value)

        # Test parsing petabytes
        assert Bytes.parse("1 PB") == pb_value

    def test_fractional_bytes(self):
        """Test handling of fractional byte values."""
        # Should round to nearest integer
        assert isinstance(Bytes.parse("1.7 KB"), int)
        assert Bytes.parse("1.7 KB") == int(1.7 * 1024)

    def test_whitespace_handling(self):
        """Test various whitespace scenarios."""
        assert Bytes.parse("  1 KB  ") == 1024
        assert Bytes.parse("\t1\tKB\t") == 1024
        assert Bytes.parse("\n1 KB\n") == 1024
