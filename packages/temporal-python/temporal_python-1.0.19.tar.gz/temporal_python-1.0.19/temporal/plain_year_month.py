"""
PlainYearMonth implementation for Temporal API in Python.
Represents a year-month combination without a specific day.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any, Dict, Optional, Union

from .calendar import Calendar
from .duration import Duration
from .exceptions import InvalidArgumentError, RangeError, TemporalError
from .utils import get_days_in_month, is_leap_year, pad_zero, validate_date_fields

if TYPE_CHECKING:
    from .plain_date import PlainDate


class PlainYearMonth:
    """
    PlainYearMonth represents a year-month combination without a specific day.
    It's useful for representing things like "February 2023" or for date calculations
    that don't need a specific day.
    """

    def __init__(self, year: int, month: int, calendar: Optional[Calendar] = None):
        """
        Initialize a PlainYearMonth.

        Args:
            year: The year (any integer)
            month: The month (1-12)
            calendar: The calendar system (defaults to ISO 8601)
        """
        validate_date_fields(year, month, 1)  # Use day=1 for validation

        self._year = year
        self._month = month
        self._calendar = calendar or Calendar.from_string("iso8601")

    @property
    def year(self) -> int:
        """The year."""
        return self._year

    @property
    def month(self) -> int:
        """The month (1-12)."""
        return self._month

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

    @property
    def days_in_month(self) -> int:
        """The number of days in this month."""
        return get_days_in_month(self._year, self._month)

    @property
    def in_leap_year(self) -> bool:
        """Whether this year is a leap year."""
        return is_leap_year(self._year)

    def add(self, duration: Duration) -> PlainYearMonth:
        """
        Add a duration to this PlainYearMonth.

        Args:
            duration: The duration to add

        Returns:
            A new PlainYearMonth with the duration added
        """
        if not isinstance(duration, Duration):
            raise InvalidArgumentError("Expected Duration")

        new_year = self._year
        new_month = self._month

        # Add years
        if duration.years:
            new_year += duration.years

        # Add months
        if duration.months:
            new_month += duration.months

            # Handle month overflow
            while new_month > 12:
                new_month -= 12
                new_year += 1
            while new_month < 1:
                new_month += 12
                new_year -= 1

        # Days, hours, minutes, seconds are not applicable for PlainYearMonth
        if any([duration.days, duration.hours, duration.minutes, duration.seconds, duration.microseconds]):
            raise InvalidArgumentError("Cannot add time units to PlainYearMonth")

        return PlainYearMonth(new_year, new_month, self._calendar)

    def subtract(self, other: Union[Duration, PlainYearMonth]) -> Union[PlainYearMonth, Duration]:
        """
        Subtract a duration or another PlainYearMonth from this PlainYearMonth.

        Args:
            other: The duration or PlainYearMonth to subtract

        Returns:
            A new PlainYearMonth (if subtracting duration) or Duration (if subtracting PlainYearMonth)
        """
        if isinstance(other, Duration):
            return self.add(other.negated())
        elif isinstance(other, PlainYearMonth):
            return other.until(self)
        else:
            raise InvalidArgumentError("Expected Duration or PlainYearMonth")

    def until(self, other: PlainYearMonth) -> Duration:
        """
        Calculate the duration from this PlainYearMonth to another.

        Args:
            other: The target PlainYearMonth

        Returns:
            A Duration representing the difference
        """
        if not isinstance(other, PlainYearMonth):
            raise InvalidArgumentError("Expected PlainYearMonth")

        years_diff = other._year - self._year
        months_diff = other._month - self._month

        # Calculate total months difference
        total_months = years_diff * 12 + months_diff

        # Convert to years and months
        if total_months >= 0:
            final_years = total_months // 12
            final_months = total_months % 12
        else:
            # Handle negative values correctly
            final_years = -((-total_months) // 12)
            final_months = -((-total_months) % 12)
            if final_months != 0:
                final_years -= 1
                final_months = 12 + final_months

        return Duration(years=final_years, months=final_months)

    def since(self, other: PlainYearMonth) -> Duration:
        """
        Calculate the duration from another PlainYearMonth to this one.

        Args:
            other: The source PlainYearMonth

        Returns:
            A Duration representing the difference
        """
        return other.until(self)

    def with_fields(self, **kwargs) -> PlainYearMonth:
        """
        Create a new PlainYearMonth with modified fields.

        Args:
            **kwargs: Fields to modify (year, month, calendar)

        Returns:
            A new PlainYearMonth with modified fields
        """
        new_year = kwargs.get("year", self._year)
        new_month = kwargs.get("month", self._month)
        new_calendar = kwargs.get("calendar", self._calendar)

        return PlainYearMonth(new_year, new_month, new_calendar)

    def to_plain_date(self, day: int) -> PlainDate:
        """
        Convert to a PlainDate by specifying a day.

        Args:
            day: The day of the month (1-31)

        Returns:
            A PlainDate with the specified day
        """
        from .plain_date import PlainDate

        return PlainDate(self._year, self._month, day, self._calendar)

    def equals(self, other: PlainYearMonth) -> bool:
        """
        Check if this PlainYearMonth equals another.

        Args:
            other: The PlainYearMonth to compare

        Returns:
            True if equal, False otherwise
        """
        if not isinstance(other, PlainYearMonth):
            return False
        return self._year == other._year and self._month == other._month and self._calendar.id == other._calendar.id

    def __str__(self) -> str:
        """String representation in ISO 8601 format (YYYY-MM)."""
        return f"{self._year:04d}-{pad_zero(self._month, 2)}"

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return f"PlainYearMonth({self._year}, {self._month}, calendar={self._calendar.id})"

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
        if not isinstance(other, PlainYearMonth):
            return NotImplemented
        return (self._year, self._month) < (other._year, other._month)

    def __le__(self, other) -> bool:
        if not isinstance(other, PlainYearMonth):
            return NotImplemented
        return (self._year, self._month) <= (other._year, other._month)

    def __gt__(self, other) -> bool:
        if not isinstance(other, PlainYearMonth):
            return NotImplemented
        return (self._year, self._month) > (other._year, other._month)

    def __ge__(self, other) -> bool:
        if not isinstance(other, PlainYearMonth):
            return NotImplemented
        return (self._year, self._month) >= (other._year, other._month)

    @staticmethod
    def from_string(year_month_string: str) -> PlainYearMonth:
        """
        Create a PlainYearMonth from an ISO 8601 string.

        Args:
            year_month_string: String in format 'YYYY-MM'

        Returns:
            A new PlainYearMonth
        """
        # Match YYYY-MM format
        pattern = r"^(\d{4})-(\d{2})$"
        match = re.match(pattern, year_month_string)

        if not match:
            raise InvalidArgumentError(f"Invalid PlainYearMonth string: {year_month_string}")

        year = int(match.group(1))
        month = int(match.group(2))

        return PlainYearMonth(year, month)

    @staticmethod
    def from_fields(fields: Dict[str, Any]) -> PlainYearMonth:
        """
        Create a PlainYearMonth from a dictionary of fields.

        Args:
            fields: Dictionary with year, month, and optional calendar

        Returns:
            A new PlainYearMonth
        """
        year = fields.get("year")
        month = fields.get("month")
        calendar = fields.get("calendar")

        if year is None or month is None:
            raise InvalidArgumentError("year and month are required")

        if calendar and isinstance(calendar, str):
            calendar = Calendar.from_string(calendar)

        return PlainYearMonth(year, month, calendar)

    @staticmethod
    def from_date(date) -> PlainYearMonth:
        """
        Create a PlainYearMonth from a date-like object.

        Args:
            date: Object with year and month attributes

        Returns:
            A new PlainYearMonth
        """
        return PlainYearMonth(date.year, date.month)

    @staticmethod
    def compare(a: PlainYearMonth, b: PlainYearMonth) -> int:
        """
        Compare two PlainYearMonth objects.

        Args:
            a: First PlainYearMonth
            b: Second PlainYearMonth

        Returns:
            -1 if a < b, 0 if a == b, 1 if a > b
        """
        if not isinstance(a, PlainYearMonth) or not isinstance(b, PlainYearMonth):
            raise InvalidArgumentError("Both arguments must be PlainYearMonth")

        if a < b:
            return -1
        elif a > b:
            return 1
        else:
            return 0

    @classmethod
    def from_any(cls, value: Union[str, dict, PlainYearMonth]) -> PlainYearMonth:
        """
        Create a PlainYearMonth from various input types.

        Args:
            value: String, dict, or PlainYearMonth

        Returns:
            A new PlainYearMonth
        """
        if isinstance(value, PlainYearMonth):
            return value
        elif isinstance(value, str):
            return cls.from_string(value)
        elif isinstance(value, dict):
            return cls.from_fields(value)
        else:
            raise InvalidArgumentError(f"Cannot create PlainYearMonth from {type(value)}")
