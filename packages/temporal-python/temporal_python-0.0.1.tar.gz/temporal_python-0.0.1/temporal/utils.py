"""
Utility functions for the Temporal API.
"""

import re
from typing import Dict, Any, Optional, Tuple
from .exceptions import InvalidArgumentError, RangeError

# ISO 8601 regex patterns
ISO_DATE_PATTERN = re.compile(
    r'^(\d{4})-(\d{2})-(\d{2})$'
)

ISO_TIME_PATTERN = re.compile(
    r'^(\d{2}):(\d{2}):(\d{2})(?:\.(\d{1,9}))?$'
)

ISO_DATETIME_PATTERN = re.compile(
    r'^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})(?:\.(\d{1,9}))?$'
)

ISO_DURATION_PATTERN = re.compile(
    r'^P(?:(\d+)Y)?(?:(\d+)M)?(?:(\d+)W)?(?:(\d+)D)?(?:T(?:(\d+)H)?(?:(\d+)M)?(?:(\d+(?:\.\d+)?)S)?)?$'
)


def validate_date_fields(year: int, month: int, day: int) -> None:
    """Validate date field values."""
    if not isinstance(year, int):
        raise InvalidArgumentError("Year must be an integer")
    if not isinstance(month, int):
        raise InvalidArgumentError("Month must be an integer")
    if not isinstance(day, int):
        raise InvalidArgumentError("Day must be an integer")
    
    if year < 1 or year > 9999:
        raise RangeError(f"Year {year} is out of range (1-9999)")
    if month < 1 or month > 12:
        raise RangeError(f"Month {month} is out of range (1-12)")
    if day < 1:
        raise RangeError(f"Day {day} is out of range (must be >= 1)")
    
    # Check day against month limits
    days_in_month = get_days_in_month(year, month)
    if day > days_in_month:
        raise RangeError(f"Day {day} is invalid for {year}-{month:02d}")


def validate_time_fields(hour: int, minute: int, second: int, microsecond: int = 0) -> None:
    """Validate time field values."""
    if not isinstance(hour, int):
        raise InvalidArgumentError("Hour must be an integer")
    if not isinstance(minute, int):
        raise InvalidArgumentError("Minute must be an integer")
    if not isinstance(second, int):
        raise InvalidArgumentError("Second must be an integer")
    if not isinstance(microsecond, int):
        raise InvalidArgumentError("Microsecond must be an integer")
    
    if hour < 0 or hour > 23:
        raise RangeError(f"Hour {hour} is out of range (0-23)")
    if minute < 0 or minute > 59:
        raise RangeError(f"Minute {minute} is out of range (0-59)")
    if second < 0 or second > 59:
        raise RangeError(f"Second {second} is out of range (0-59)")
    if microsecond < 0 or microsecond > 999999:
        raise RangeError(f"Microsecond {microsecond} is out of range (0-999999)")


def is_leap_year(year: int) -> bool:
    """Check if a year is a leap year."""
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def get_days_in_month(year: int, month: int) -> int:
    """Get the number of days in a given month and year."""
    days_in_months = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    days = days_in_months[month - 1]
    if month == 2 and is_leap_year(year):
        days = 29
    return days


def parse_iso_date(date_string: str) -> Tuple[int, int, int]:
    """Parse an ISO 8601 date string."""
    match = ISO_DATE_PATTERN.match(date_string)
    if not match:
        raise InvalidArgumentError(f"Invalid ISO date format: {date_string}")
    
    year, month, day = map(int, match.groups())
    validate_date_fields(year, month, day)
    return year, month, day


def parse_iso_time(time_string: str) -> Tuple[int, int, int, int]:
    """Parse an ISO 8601 time string."""
    match = ISO_TIME_PATTERN.match(time_string)
    if not match:
        raise InvalidArgumentError(f"Invalid ISO time format: {time_string}")
    
    hour, minute, second, fraction = match.groups()
    hour, minute, second = int(hour), int(minute), int(second)
    
    microsecond = 0
    if fraction:
        # Pad or truncate to 6 digits for microseconds
        fraction = fraction.ljust(6, '0')[:6]
        microsecond = int(fraction)
    
    validate_time_fields(hour, minute, second, microsecond)
    return hour, minute, second, microsecond


def parse_iso_datetime(datetime_string: str) -> Tuple[int, int, int, int, int, int, int]:
    """Parse an ISO 8601 datetime string."""
    match = ISO_DATETIME_PATTERN.match(datetime_string)
    if not match:
        raise InvalidArgumentError(f"Invalid ISO datetime format: {datetime_string}")
    
    year, month, day, hour, minute, second, fraction = match.groups()
    year, month, day = int(year), int(month), int(day)
    hour, minute, second = int(hour), int(minute), int(second)
    
    microsecond = 0
    if fraction:
        fraction = fraction.ljust(6, '0')[:6]
        microsecond = int(fraction)
    
    validate_date_fields(year, month, day)
    validate_time_fields(hour, minute, second, microsecond)
    return year, month, day, hour, minute, second, microsecond


def pad_zero(value: int, width: int = 2) -> str:
    """Pad a number with leading zeros."""
    return str(value).zfill(width)


def format_microseconds(microsecond: int) -> str:
    """Format microseconds, removing trailing zeros."""
    if microsecond == 0:
        return ""
    return f".{microsecond:06d}".rstrip('0')
