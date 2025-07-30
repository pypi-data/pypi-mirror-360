"""Date and time utility functions.

This module provides utility functions for working with dates and times,
porting JavaScript Date object methods and other date utilities to Python.
"""

import datetime
import time


def now() -> int:
    """Get current timestamp in milliseconds.

    Similar to JavaScript Date.now().

    Returns:
        Current timestamp in milliseconds

    Examples:
        >>> timestamp = now()
        >>> isinstance(timestamp, int)
        True
        >>> timestamp > 0
        True
    """
    return int(time.time() * 1000)


def parse_date(date_string: str) -> datetime.datetime:
    """Parse a date string into a datetime object (like JavaScript Date.parse()).

    Args:
        date_string: Date string to parse

    Returns:
        Parsed datetime object

    Raises:
        ValueError: If date string cannot be parsed

    Examples:
        >>> parse_date('2023-01-01')
        datetime.datetime(2023, 1, 1, 0, 0)
        >>> parse_date('2023-01-01T12:30:45')
        datetime.datetime(2023, 1, 1, 12, 30, 45)
    """
    # Try common date formats
    formats = [
        "%Y-%m-%d",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
        "%Y/%m/%d",
        "%m/%d/%Y",
        "%d/%m/%Y",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%dT%H:%M:%SZ",
    ]

    for fmt in formats:
        try:
            return datetime.datetime.strptime(date_string, fmt)
        except ValueError:
            continue

    raise ValueError(f"Unable to parse date string: {date_string}")


def to_iso_string(dt: datetime.datetime) -> str:
    """Convert datetime to ISO string (like JavaScript Date.toISOString()).

    Args:
        dt: Datetime object to convert

    Returns:
        ISO format string

    Examples:
        >>> dt = datetime.datetime(2023, 1, 1, 12, 30, 45)
        >>> to_iso_string(dt)
        '2023-01-01T12:30:45'
    """
    return dt.isoformat()


def to_date_string(dt: datetime.datetime) -> str:
    """Convert datetime to date string (like JavaScript Date.toDateString()).

    Args:
        dt: Datetime object to convert

    Returns:
        Date string in format 'YYYY-MM-DD'

    Examples:
        >>> dt = datetime.datetime(2023, 1, 1, 12, 30, 45)
        >>> to_date_string(dt)
        '2023-01-01'
    """
    return dt.strftime("%Y-%m-%d")


def to_time_string(dt: datetime.datetime) -> str:
    """Convert datetime to time string (like JavaScript Date.toTimeString()).

    Args:
        dt: Datetime object to convert

    Returns:
        Time string in format 'HH:MM:SS'

    Examples:
        >>> dt = datetime.datetime(2023, 1, 1, 12, 30, 45)
        >>> to_time_string(dt)
        '12:30:45'
    """
    return dt.strftime("%H:%M:%S")


def get_time(dt: datetime.datetime) -> int:
    """Get timestamp in milliseconds from datetime (like JavaScript Date.getTime()).

    Args:
        dt: Datetime object

    Returns:
        Timestamp in milliseconds

    Examples:
        >>> dt = datetime.datetime(2023, 1, 1, 0, 0, 0)
        >>> timestamp = get_time(dt)
        >>> isinstance(timestamp, int)
        True
    """
    return int(dt.timestamp() * 1000)


def add_days(dt: datetime.datetime, days: int) -> datetime.datetime:
    """Add days to a datetime object.

    Args:
        dt: Base datetime
        days: Number of days to add (can be negative)

    Returns:
        New datetime with days added

    Examples:
        >>> dt = datetime.datetime(2023, 1, 1)
        >>> add_days(dt, 5)
        datetime.datetime(2023, 1, 6, 0, 0)
        >>> add_days(dt, -1)
        datetime.datetime(2022, 12, 31, 0, 0)
    """
    return dt + datetime.timedelta(days=days)


def add_hours(dt: datetime.datetime, hours: int) -> datetime.datetime:
    """Add hours to a datetime object.

    Args:
        dt: Base datetime
        hours: Number of hours to add (can be negative)

    Returns:
        New datetime with hours added

    Examples:
        >>> dt = datetime.datetime(2023, 1, 1, 12, 0, 0)
        >>> add_hours(dt, 3)
        datetime.datetime(2023, 1, 1, 15, 0)
        >>> add_hours(dt, -2)
        datetime.datetime(2023, 1, 1, 10, 0)
    """
    return dt + datetime.timedelta(hours=hours)


def add_minutes(dt: datetime.datetime, minutes: int) -> datetime.datetime:
    """Add minutes to a datetime object.

    Args:
        dt: Base datetime
        minutes: Number of minutes to add (can be negative)

    Returns:
        New datetime with minutes added

    Examples:
        >>> dt = datetime.datetime(2023, 1, 1, 12, 30, 0)
        >>> add_minutes(dt, 15)
        datetime.datetime(2023, 1, 1, 12, 45)
        >>> add_minutes(dt, -10)
        datetime.datetime(2023, 1, 1, 12, 20)
    """
    return dt + datetime.timedelta(minutes=minutes)


def format_relative_time(
    dt: datetime.datetime, base_dt: datetime.datetime | None = None
) -> str:
    """Format datetime as relative time string (like 'X minutes ago').

    Args:
        dt: Datetime to format
        base_dt: Base datetime to compare against (defaults to now)

    Returns:
        Relative time string

    Examples:
        >>> import datetime
        >>> now = datetime.datetime.now()
        >>> past = now - datetime.timedelta(minutes=5)
        >>> format_relative_time(past, now)
        '5 minutes ago'
    """
    if base_dt is None:
        base_dt = datetime.datetime.now()

    diff = base_dt - dt
    total_seconds = int(diff.total_seconds())

    if total_seconds < 0:
        # Future time
        total_seconds = abs(total_seconds)
        suffix = "from now"
    else:
        suffix = "ago"

    if total_seconds < 60:
        return f"{total_seconds} seconds {suffix}"
    elif total_seconds < 3600:
        minutes = total_seconds // 60
        return f"{minutes} minutes {suffix}"
    elif total_seconds < 86400:
        hours = total_seconds // 3600
        return f"{hours} hours {suffix}"
    else:
        days = total_seconds // 86400
        return f"{days} days {suffix}"


def is_valid_date(date_string: str) -> bool:
    """Check if a string represents a valid date.

    Args:
        date_string: String to check

    Returns:
        True if valid date, False otherwise

    Examples:
        >>> is_valid_date('2023-01-01')
        True
        >>> is_valid_date('invalid-date')
        False
        >>> is_valid_date('2023-13-01')  # Invalid month
        False
    """
    try:
        parse_date(date_string)
        return True
    except ValueError:
        return False
