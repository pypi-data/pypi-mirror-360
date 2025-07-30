"""
PlainDate implementation for the Temporal API.
"""

from datetime import date
from typing import TYPE_CHECKING, Optional, Union

from .calendar import Calendar
from .exceptions import InvalidArgumentError, RangeError
from .utils import get_days_in_month, pad_zero, parse_iso_date, validate_date_fields

if TYPE_CHECKING:
    from .duration import Duration
    from .plain_date_time import PlainDateTime
    from .plain_month_day import PlainMonthDay
    from .plain_year_month import PlainYearMonth
    from .zoned_date_time import ZonedDateTime


class PlainDate:
    """Represents a date without time zone information."""

    def __init__(self, year: int, month: int, day: int, calendar: Optional[Calendar] = None):
        """Initialize a PlainDate with year, month, and day."""
        validate_date_fields(year, month, day)

        self._year = year
        self._month = month
        self._day = day
        self._calendar = calendar or Calendar()

    @property
    def year(self) -> int:
        """Get the year."""
        return self._year

    @property
    def month(self) -> int:
        """Get the month (1-12)."""
        return self._month

    @property
    def day(self) -> int:
        """Get the day of the month."""
        return self._day

    @property
    def calendar(self) -> Calendar:
        """Get the calendar."""
        return self._calendar

    @property
    def day_of_week(self) -> int:
        """Get the day of the week (1=Monday, 7=Sunday)."""
        # Use datetime to calculate day of week
        dt = date(self._year, self._month, self._day)
        return dt.isoweekday()

    @property
    def day_of_year(self) -> int:
        """Get the day of the year (1-366)."""
        dt = date(self._year, self._month, self._day)
        return dt.timetuple().tm_yday

    @property
    def week_of_year(self) -> int:
        """Get the ISO week number."""
        dt = date(self._year, self._month, self._day)
        return dt.isocalendar()[1]

    def add(self, duration) -> "PlainDate":
        """Add a duration to this date."""
        from .duration import Duration

        if not isinstance(duration, Duration):
            raise InvalidArgumentError("Expected Duration object")

        new_year = self._year + duration.years
        new_month = self._month + duration.months
        new_day = self._day

        # Handle month overflow/underflow
        while new_month > 12:
            new_year += 1
            new_month -= 12
        while new_month < 1:
            new_year -= 1
            new_month += 12

        # Clamp day to valid range for the target month first
        max_day = get_days_in_month(new_year, new_month)
        if new_day > max_day:
            new_day = max_day

        # Now add the days
        new_day += duration.days

        # Handle day overflow by properly carrying to next month
        while new_day > get_days_in_month(new_year, new_month):
            new_day -= get_days_in_month(new_year, new_month)
            new_month += 1
            if new_month > 12:
                new_year += 1
                new_month = 1

        # Handle day underflow
        while new_day < 1:
            new_month -= 1
            if new_month < 1:
                new_year -= 1
                new_month = 12
            new_day += get_days_in_month(new_year, new_month)

        return PlainDate(new_year, new_month, new_day, self._calendar)

    def subtract(self, other) -> Union["PlainDate", "Duration"]:
        """Subtract another date or duration from this date."""
        from .duration import Duration

        if isinstance(other, Duration):
            # Subtract duration - negate and add
            negated_duration = Duration(
                -other.years,
                -other.months,
                -other.weeks,
                -other.days,
                -other.hours,
                -other.minutes,
                -other.seconds,
                -other.microseconds,
            )
            return self.add(negated_duration)
        elif isinstance(other, PlainDate):
            # Subtract date - return duration
            dt1 = date(self._year, self._month, self._day)
            dt2 = date(other._year, other._month, other._day)
            delta = dt1 - dt2
            return Duration(days=delta.days)
        else:
            raise InvalidArgumentError("Expected PlainDate or Duration object")

    def with_fields(
        self,
        *,
        year: Optional[int] = None,
        month: Optional[int] = None,
        day: Optional[int] = None,
        calendar: Optional[Calendar] = None,
    ) -> "PlainDate":
        """Return a new PlainDate with specified fields replaced."""
        new_year = year if year is not None else self._year
        new_month = month if month is not None else self._month
        new_day = day if day is not None else self._day
        new_calendar = calendar if calendar is not None else self._calendar

        return PlainDate(new_year, new_month, new_day, new_calendar)

    def to_plain_datetime(self, time=None) -> "PlainDateTime":
        """Convert to PlainDateTime by adding time."""
        from .plain_date_time import PlainDateTime
        from .plain_time import PlainTime

        if time is None:
            time = PlainTime(0, 0, 0)
        elif not isinstance(time, PlainTime):
            raise InvalidArgumentError("Expected PlainTime object")

        return PlainDateTime(
            self._year, self._month, self._day, time.hour, time.minute, time.second, time.microsecond, self._calendar
        )

    def __str__(self) -> str:
        """Return ISO 8601 string representation."""
        return f"{self._year:04d}-{pad_zero(self._month)}-{pad_zero(self._day)}"

    def __repr__(self) -> str:
        """Return detailed string representation."""
        return f"PlainDate({self._year}, {self._month}, {self._day})"

    def __eq__(self, other) -> bool:
        """Check equality with another PlainDate."""
        if not isinstance(other, PlainDate):
            return False
        return self._year == other._year and self._month == other._month and self._day == other._day

    def __lt__(self, other) -> bool:
        """Check if this date is less than another."""
        if not isinstance(other, PlainDate):
            raise InvalidArgumentError("Expected PlainDate object")
        return (self._year, self._month, self._day) < (other._year, other._month, other._day)

    def __le__(self, other) -> bool:
        """Check if this date is less than or equal to another."""
        return self == other or self < other

    def __gt__(self, other) -> bool:
        """Check if this date is greater than another."""
        return not self <= other

    def __ge__(self, other) -> bool:
        """Check if this date is greater than or equal to another."""
        return not self < other

    def __hash__(self) -> int:
        """Hash function for PlainDate."""
        return hash((self._year, self._month, self._day))

    @classmethod
    def from_string(cls, date_string: str, calendar: Optional[Calendar] = None) -> "PlainDate":
        """Create PlainDate from ISO 8601 string."""
        year, month, day = parse_iso_date(date_string)
        return cls(year, month, day, calendar)

    @classmethod
    def today(cls, calendar: Optional[Calendar] = None) -> "PlainDate":
        """Get today's date."""
        today = date.today()
        return cls(today.year, today.month, today.day, calendar)

    def until(self, other: "PlainDate") -> "Duration":
        """Calculate duration from this date to another.

        Args:
            other: The target date

        Returns:
            A Duration representing the difference
        """
        if not isinstance(other, PlainDate):
            raise InvalidArgumentError("Expected PlainDate")

        return other.subtract(self)  # type: ignore[return-value]

    def since(self, other: "PlainDate") -> "Duration":
        """Calculate duration from another date to this one.

        Args:
            other: The source date

        Returns:
            A Duration representing the difference
        """
        if not isinstance(other, PlainDate):
            raise InvalidArgumentError("Expected PlainDate")

        return self.subtract(other)  # type: ignore[return-value]

    def to_plain_year_month(self) -> "PlainYearMonth":
        """Convert to PlainYearMonth.

        Returns:
            A PlainYearMonth with this date's year and month
        """
        from .plain_year_month import PlainYearMonth

        return PlainYearMonth(self._year, self._month, self._calendar)

    def to_plain_month_day(self) -> "PlainMonthDay":
        """Convert to PlainMonthDay.

        Returns:
            A PlainMonthDay with this date's month and day
        """
        from .plain_month_day import PlainMonthDay

        return PlainMonthDay(self._month, self._day, self._calendar)

    def to_zoned_date_time(self, timezone, time=None) -> "ZonedDateTime":
        """Convert to ZonedDateTime by adding timezone and optional time.

        Args:
            timezone: The timezone to use
            time: Optional time (defaults to midnight)

        Returns:
            A ZonedDateTime
        """
        from .plain_time import PlainTime
        from .zoned_date_time import ZonedDateTime

        if time is None:
            time = PlainTime(0, 0, 0)

        return ZonedDateTime(
            self._year, self._month, self._day, time.hour, time.minute, time.second, time.microsecond, timezone
        )

    def equals(self, other: "PlainDate") -> bool:
        """Check if this date equals another.

        Args:
            other: The date to compare

        Returns:
            True if equal, False otherwise
        """
        return self == other

    def to_json(self) -> str:
        """Convert to JSON string."""
        return str(self)

    def to_locale_string(self, locale: str = "en-US") -> str:
        """Convert to locale-specific string representation."""
        # Basic implementation - could be enhanced with full locale support
        return str(self)

    @staticmethod
    def compare(a: "PlainDate", b: "PlainDate") -> int:
        """Compare two PlainDate objects.

        Args:
            a: First PlainDate
            b: Second PlainDate

        Returns:
            -1 if a < b, 0 if a == b, 1 if a > b
        """
        if not isinstance(a, PlainDate) or not isinstance(b, PlainDate):
            raise InvalidArgumentError("Both arguments must be PlainDate")

        if a < b:
            return -1
        elif a > b:
            return 1
        else:
            return 0

    @classmethod
    def from_any(cls, value: Union[str, dict, "PlainDate"]) -> "PlainDate":
        """Create a PlainDate from various input types.

        Args:
            value: String, dict, or PlainDate

        Returns:
            A new PlainDate
        """
        if isinstance(value, PlainDate):
            return value
        elif isinstance(value, str):
            return cls.from_string(value)
        elif isinstance(value, dict):
            year = value.get("year")
            month = value.get("month")
            day = value.get("day")
            calendar = value.get("calendar")

            if year is None or month is None or day is None:
                raise InvalidArgumentError("year, month, and day are required")

            if calendar and isinstance(calendar, str):
                calendar = Calendar.from_string(calendar)

            return cls(year, month, day, calendar)
        else:
            raise InvalidArgumentError(f"Cannot create PlainDate from {type(value)}")
