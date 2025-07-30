"""Tests for date utility functions."""

import datetime

import pytest

from pyutils.date import (
    add_days,
    add_hours,
    add_minutes,
    format_relative_time,
    get_time,
    is_valid_date,
    now,
    parse_date,
    to_date_string,
    to_iso_string,
    to_time_string,
)


class TestDateUtils:
    """Test date utility functions."""

    def test_now(self):
        """Test now function."""
        timestamp = now()
        assert isinstance(timestamp, int)
        assert timestamp > 0
        # Should be close to current time (within 1 second)
        current_time = int(datetime.datetime.now().timestamp() * 1000)
        assert abs(timestamp - current_time) < 1000

    def test_parse_date_valid_formats(self):
        """Test parse_date with valid date formats."""
        # Test various date formats
        test_cases = [
            ("2023-01-01", datetime.datetime(2023, 1, 1, 0, 0)),
            ("2023-01-01T12:30:45", datetime.datetime(2023, 1, 1, 12, 30, 45)),
            ("2023-01-01 12:30:45", datetime.datetime(2023, 1, 1, 12, 30, 45)),
            ("2023/01/01", datetime.datetime(2023, 1, 1, 0, 0)),
            ("01/01/2023", datetime.datetime(2023, 1, 1, 0, 0)),
        ]

        for date_string, expected in test_cases:
            result = parse_date(date_string)
            assert result == expected

    def test_parse_date_invalid_format(self):
        """Test parse_date with invalid date format."""
        with pytest.raises(ValueError, match="Unable to parse date string"):
            parse_date("invalid-date")

        with pytest.raises(ValueError):
            parse_date("2023-13-01")  # Invalid month

    def test_to_iso_string(self):
        """Test to_iso_string function."""
        dt = datetime.datetime(2023, 1, 1, 12, 30, 45)
        result = to_iso_string(dt)
        assert result == "2023-01-01T12:30:45"

    def test_to_date_string(self):
        """Test to_date_string function."""
        dt = datetime.datetime(2023, 1, 1, 12, 30, 45)
        result = to_date_string(dt)
        assert result == "2023-01-01"

    def test_to_time_string(self):
        """Test to_time_string function."""
        dt = datetime.datetime(2023, 1, 1, 12, 30, 45)
        result = to_time_string(dt)
        assert result == "12:30:45"

    def test_get_time(self):
        """Test get_time function."""
        dt = datetime.datetime(2023, 1, 1, 0, 0, 0)
        timestamp = get_time(dt)
        assert isinstance(timestamp, int)
        # Should be positive timestamp
        assert timestamp > 0

    def test_add_days(self):
        """Test add_days function."""
        dt = datetime.datetime(2023, 1, 1)

        # Add positive days
        result = add_days(dt, 5)
        assert result == datetime.datetime(2023, 1, 6)

        # Add negative days
        result = add_days(dt, -1)
        assert result == datetime.datetime(2022, 12, 31)

        # Add zero days
        result = add_days(dt, 0)
        assert result == dt

    def test_add_hours(self):
        """Test add_hours function."""
        dt = datetime.datetime(2023, 1, 1, 12, 0, 0)

        # Add positive hours
        result = add_hours(dt, 3)
        assert result == datetime.datetime(2023, 1, 1, 15, 0, 0)

        # Add negative hours
        result = add_hours(dt, -2)
        assert result == datetime.datetime(2023, 1, 1, 10, 0, 0)

        # Test hour overflow
        result = add_hours(dt, 15)
        assert result == datetime.datetime(2023, 1, 2, 3, 0, 0)

    def test_add_minutes(self):
        """Test add_minutes function."""
        dt = datetime.datetime(2023, 1, 1, 12, 30, 0)

        # Add positive minutes
        result = add_minutes(dt, 15)
        assert result == datetime.datetime(2023, 1, 1, 12, 45, 0)

        # Add negative minutes
        result = add_minutes(dt, -10)
        assert result == datetime.datetime(2023, 1, 1, 12, 20, 0)

        # Test minute overflow
        result = add_minutes(dt, 45)
        assert result == datetime.datetime(2023, 1, 1, 13, 15, 0)

    def test_format_relative_time(self):
        """Test format_relative_time function."""
        base_dt = datetime.datetime(2023, 1, 1, 12, 0, 0)

        # Test seconds ago
        past_dt = base_dt - datetime.timedelta(seconds=30)
        result = format_relative_time(past_dt, base_dt)
        assert result == "30 seconds ago"

        # Test minutes ago
        past_dt = base_dt - datetime.timedelta(minutes=5)
        result = format_relative_time(past_dt, base_dt)
        assert result == "5 minutes ago"

        # Test hours ago
        past_dt = base_dt - datetime.timedelta(hours=2)
        result = format_relative_time(past_dt, base_dt)
        assert result == "2 hours ago"

        # Test days ago
        past_dt = base_dt - datetime.timedelta(days=3)
        result = format_relative_time(past_dt, base_dt)
        assert result == "3 days ago"

        # Test future time
        future_dt = base_dt + datetime.timedelta(minutes=10)
        result = format_relative_time(future_dt, base_dt)
        assert result == "10 minutes from now"

    def test_is_valid_date(self):
        """Test is_valid_date function."""
        # Valid dates
        assert is_valid_date("2023-01-01") is True
        assert is_valid_date("2023-01-01T12:30:45") is True
        assert is_valid_date("2023/01/01") is True

        # Invalid dates
        assert is_valid_date("invalid-date") is False
        assert is_valid_date("2023-13-01") is False  # Invalid month
        assert is_valid_date("2023-01-32") is False  # Invalid day
        assert is_valid_date("") is False
        assert is_valid_date("not a date") is False

    def test_edge_cases(self):
        """Test edge cases."""
        # Test leap year
        leap_year_date = parse_date("2024-02-29")
        assert leap_year_date.year == 2024
        assert leap_year_date.month == 2
        assert leap_year_date.day == 29

        # Test end of year
        end_of_year = datetime.datetime(2023, 12, 31, 23, 59, 59)
        next_year = add_days(end_of_year, 1)
        assert next_year.year == 2024
        assert next_year.month == 1
        assert next_year.day == 1
