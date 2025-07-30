"""
PlainMonthDay implementation for Temporal API in Python.
Represents a month-day combination without a year.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any, Dict, Optional, Union

from .calendar import Calendar
from .exceptions import InvalidArgumentError, RangeError, TemporalError
from .utils import get_days_in_month, pad_zero, validate_date_fields

if TYPE_CHECKING:
    from .plain_date import PlainDate


class PlainMonthDay:
    """
    PlainMonthDay represents a month-day combination without a year.
    It's useful for representing recurring dates like birthdays, anniversaries,
    or holidays that occur on the same month-day each year.
    """

    def __init__(self, month: int, day: int, calendar: Optional[Calendar] = None):
        """
        Initialize a PlainMonthDay.

        Args:
            month: The month (1-12)
            day: The day of the month (1-31)
            calendar: The calendar system (defaults to ISO 8601)
        """
        # Use year 2000 (a leap year) for validation to allow Feb 29
        validate_date_fields(2000, month, day)

        # Additional validation for February 29 in non-leap years
        if month == 2 and day == 29:
            # This is valid for PlainMonthDay, but we need to handle it specially
            # when converting to a specific year
            pass
        elif month == 2 and day > 29:
            raise RangeError(f"Day {day} is invalid for February")
        elif day > get_days_in_month(2000, month):
            raise RangeError(f"Day {day} is invalid for month {month}")

        self._month = month
        self._day = day
        self._calendar = calendar or Calendar.from_string("iso8601")

    @property
    def month(self) -> int:
        """The month (1-12)."""
        return self._month

    @property
    def day(self) -> int:
        """The day of the month (1-31)."""
        return self._day

    @property
    def month_code(self) -> str:
        """The month code (e.g., 'M02' for February)."""
        return f"M{pad_zero(self._month, 2)}"

    @property
    def calendar(self) -> Calendar:
        """The calendar system."""
        return self._calendar

    @property
    def calendar_id(self) -> str:
        """The calendar system identifier."""
        return self._calendar.id

    def with_fields(self, **kwargs) -> PlainMonthDay:
        """
        Create a new PlainMonthDay with modified fields.

        Args:
            **kwargs: Fields to modify (month, day, calendar)

        Returns:
            A new PlainMonthDay with modified fields
        """
        new_month = kwargs.get("month", self._month)
        new_day = kwargs.get("day", self._day)
        new_calendar = kwargs.get("calendar", self._calendar)

        return PlainMonthDay(new_month, new_day, new_calendar)

    def to_plain_date(self, year: int) -> PlainDate:
        """
        Convert to a PlainDate by specifying a year.

        Args:
            year: The year to use

        Returns:
            A PlainDate with the specified year

        Raises:
            RangeError: If the month-day combination is invalid for the given year
                       (e.g., February 29 in a non-leap year)
        """
        from .plain_date import PlainDate
        from .utils import is_leap_year

        # Check if February 29 is valid for this year
        if self._month == 2 and self._day == 29 and not is_leap_year(year):
            raise RangeError(f"February 29 is not valid in year {year} (not a leap year)")

        return PlainDate(year, self._month, self._day, self._calendar)

    def equals(self, other: PlainMonthDay) -> bool:
        """
        Check if this PlainMonthDay equals another.

        Args:
            other: The PlainMonthDay to compare

        Returns:
            True if equal, False otherwise
        """
        if not isinstance(other, PlainMonthDay):
            return False
        return self._month == other._month and self._day == other._day and self._calendar.id == other._calendar.id

    def __str__(self) -> str:
        """String representation in ISO 8601 format (--MM-DD)."""
        return f"--{pad_zero(self._month, 2)}-{pad_zero(self._day, 2)}"

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return f"PlainMonthDay({self._month}, {self._day}, calendar={self._calendar.id})"

    def to_json(self) -> str:
        """Convert to JSON string."""
        return str(self)

    def to_locale_string(self, locale: str = "en-US") -> str:
        """Convert to locale-specific string representation."""
        # Basic implementation - could be enhanced with full locale support
        return str(self)

    # Comparison operators
    def __eq__(self, other) -> bool:
        return self.equals(other)

    def __ne__(self, other) -> bool:
        return not self.equals(other)

    def __lt__(self, other) -> bool:
        if not isinstance(other, PlainMonthDay):
            return NotImplemented
        return (self._month, self._day) < (other._month, other._day)

    def __le__(self, other) -> bool:
        if not isinstance(other, PlainMonthDay):
            return NotImplemented
        return (self._month, self._day) <= (other._month, other._day)

    def __gt__(self, other) -> bool:
        if not isinstance(other, PlainMonthDay):
            return NotImplemented
        return (self._month, self._day) > (other._month, other._day)

    def __ge__(self, other) -> bool:
        if not isinstance(other, PlainMonthDay):
            return NotImplemented
        return (self._month, self._day) >= (other._month, other._day)

    @staticmethod
    def from_string(month_day_string: str) -> PlainMonthDay:
        """
        Create a PlainMonthDay from an ISO 8601 string.

        Args:
            month_day_string: String in format '--MM-DD' or 'MM-DD'

        Returns:
            A new PlainMonthDay
        """
        # Match --MM-DD or MM-DD format
        pattern = r"^(?:--)?(\d{1,2})-(\d{1,2})$"
        match = re.match(pattern, month_day_string)

        if not match:
            raise InvalidArgumentError(f"Invalid PlainMonthDay string: {month_day_string}")

        month = int(match.group(1))
        day = int(match.group(2))

        return PlainMonthDay(month, day)

    @staticmethod
    def from_fields(fields: Dict[str, Any]) -> PlainMonthDay:
        """
        Create a PlainMonthDay from a dictionary of fields.

        Args:
            fields: Dictionary with month, day, and optional calendar

        Returns:
            A new PlainMonthDay
        """
        month = fields.get("month")
        day = fields.get("day")
        calendar = fields.get("calendar")

        if month is None or day is None:
            raise InvalidArgumentError("month and day are required")

        if calendar and isinstance(calendar, str):
            calendar = Calendar.from_string(calendar)

        return PlainMonthDay(month, day, calendar)

    @staticmethod
    def from_date(date) -> PlainMonthDay:
        """
        Create a PlainMonthDay from a date-like object.

        Args:
            date: Object with month and day attributes

        Returns:
            A new PlainMonthDay
        """
        return PlainMonthDay(date.month, date.day)

    @staticmethod
    def compare(a: PlainMonthDay, b: PlainMonthDay) -> int:
        """
        Compare two PlainMonthDay objects.

        Args:
            a: First PlainMonthDay
            b: Second PlainMonthDay

        Returns:
            -1 if a < b, 0 if a == b, 1 if a > b
        """
        if not isinstance(a, PlainMonthDay) or not isinstance(b, PlainMonthDay):
            raise InvalidArgumentError("Both arguments must be PlainMonthDay")

        if a < b:
            return -1
        elif a > b:
            return 1
        else:
            return 0

    @classmethod
    def from_any(cls, value: Union[str, dict, PlainMonthDay]) -> PlainMonthDay:
        """
        Create a PlainMonthDay from various input types.

        Args:
            value: String, dict, or PlainMonthDay

        Returns:
            A new PlainMonthDay
        """
        if isinstance(value, PlainMonthDay):
            return value
        elif isinstance(value, str):
            return cls.from_string(value)
        elif isinstance(value, dict):
            return cls.from_fields(value)
        else:
            raise InvalidArgumentError(f"Cannot create PlainMonthDay from {type(value)}")

    def is_valid_for_year(self, year: int) -> bool:
        """
        Check if this PlainMonthDay is valid for a given year.

        Args:
            year: The year to check

        Returns:
            True if valid, False if invalid (e.g., Feb 29 in non-leap year)
        """
        from .utils import is_leap_year

        if self._month == 2 and self._day == 29:
            return is_leap_year(year)
        return True

    def get_valid_year(self, reference_year: int) -> int:
        """
        Get a valid year for this PlainMonthDay, adjusting if necessary.

        Args:
            reference_year: The preferred year

        Returns:
            A year where this PlainMonthDay is valid
        """
        if self.is_valid_for_year(reference_year):
            return reference_year

        # If Feb 29 in non-leap year, find the next leap year
        if self._month == 2 and self._day == 29:
            # Find the next leap year
            year = reference_year
            while not self.is_valid_for_year(year):
                year += 1
            return year

        return reference_year
