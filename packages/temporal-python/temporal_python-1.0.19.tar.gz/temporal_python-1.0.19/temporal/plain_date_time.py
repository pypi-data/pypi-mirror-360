"""
PlainDateTime implementation for the Temporal API.
"""

from datetime import datetime
from typing import TYPE_CHECKING, Optional, Union

from .calendar import Calendar
from .exceptions import InvalidArgumentError
from .utils import format_microseconds, pad_zero, parse_iso_datetime, validate_date_fields, validate_time_fields

if TYPE_CHECKING:
    from .duration import Duration
    from .plain_date import PlainDate
    from .plain_time import PlainTime
    from .zoned_date_time import ZonedDateTime


class PlainDateTime:
    """Represents a date and time without time zone information."""

    def __init__(
        self,
        year: int,
        month: int,
        day: int,
        hour: int = 0,
        minute: int = 0,
        second: int = 0,
        microsecond: int = 0,
        calendar: Optional[Calendar] = None,
    ):
        """Initialize a PlainDateTime with date and time components."""
        validate_date_fields(year, month, day)
        validate_time_fields(hour, minute, second, microsecond)

        self._year = year
        self._month = month
        self._day = day
        self._hour = hour
        self._minute = minute
        self._second = second
        self._microsecond = microsecond
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
    def hour(self) -> int:
        """Get the hour (0-23)."""
        return self._hour

    @property
    def minute(self) -> int:
        """Get the minute (0-59)."""
        return self._minute

    @property
    def second(self) -> int:
        """Get the second (0-59)."""
        return self._second

    @property
    def microsecond(self) -> int:
        """Get the microsecond (0-999999)."""
        return self._microsecond

    @property
    def calendar(self) -> Calendar:
        """Get the calendar."""
        return self._calendar

    @property
    def day_of_week(self) -> int:
        """Get the day of the week (1=Monday, 7=Sunday)."""
        dt = datetime(self._year, self._month, self._day)
        return dt.isoweekday()

    def to_plain_date(self) -> "PlainDate":
        """Extract the date part."""
        from .plain_date import PlainDate

        return PlainDate(self._year, self._month, self._day, self._calendar)

    def to_plain_time(self) -> "PlainTime":
        """Extract the time part."""
        from .plain_time import PlainTime

        return PlainTime(self._hour, self._minute, self._second, self._microsecond)

    def to_zoned_date_time(self, timezone) -> "ZonedDateTime":
        """Convert to ZonedDateTime with the given timezone."""
        from .zoned_date_time import ZonedDateTime

        return ZonedDateTime(
            self._year,
            self._month,
            self._day,
            self._hour,
            self._minute,
            self._second,
            self._microsecond,
            timezone,
            self._calendar,
        )

    def add(self, duration) -> "PlainDateTime":
        """Add a duration to this datetime."""
        from .duration import Duration

        if not isinstance(duration, Duration):
            raise InvalidArgumentError("Expected Duration object")

        # Add date components
        date_part = self.to_plain_date().add(duration)

        # Add time components
        time_part = self.to_plain_time().add(duration)

        return PlainDateTime(
            date_part.year,
            date_part.month,
            date_part.day,
            time_part.hour,
            time_part.minute,
            time_part.second,
            time_part.microsecond,
            self._calendar,
        )

    def subtract(self, other) -> Union["PlainDateTime", "Duration"]:
        """Subtract another datetime or duration from this datetime."""
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
        elif isinstance(other, PlainDateTime):
            # Subtract datetime - return duration
            dt1 = datetime(self._year, self._month, self._day, self._hour, self._minute, self._second, self._microsecond)
            dt2 = datetime(
                other._year, other._month, other._day, other._hour, other._minute, other._second, other._microsecond
            )
            delta = dt1 - dt2

            return Duration(days=delta.days, seconds=delta.seconds, microseconds=delta.microseconds)
        else:
            raise InvalidArgumentError("Expected PlainDateTime or Duration object")

    def with_fields(
        self,
        *,
        year: Optional[int] = None,
        month: Optional[int] = None,
        day: Optional[int] = None,
        hour: Optional[int] = None,
        minute: Optional[int] = None,
        second: Optional[int] = None,
        microsecond: Optional[int] = None,
        calendar: Optional[Calendar] = None,
    ) -> "PlainDateTime":
        """Return a new PlainDateTime with specified fields replaced."""
        new_year = year if year is not None else self._year
        new_month = month if month is not None else self._month
        new_day = day if day is not None else self._day
        new_hour = hour if hour is not None else self._hour
        new_minute = minute if minute is not None else self._minute
        new_second = second if second is not None else self._second
        new_microsecond = microsecond if microsecond is not None else self._microsecond
        new_calendar = calendar if calendar is not None else self._calendar

        return PlainDateTime(new_year, new_month, new_day, new_hour, new_minute, new_second, new_microsecond, new_calendar)

    def __str__(self) -> str:
        """Return ISO 8601 string representation."""
        date_str = f"{self._year:04d}-{pad_zero(self._month)}-{pad_zero(self._day)}"
        time_str = f"{pad_zero(self._hour)}:{pad_zero(self._minute)}:{pad_zero(self._second)}"
        if self._microsecond:
            time_str += format_microseconds(self._microsecond)
        return f"{date_str}T{time_str}"

    def __repr__(self) -> str:
        """Return detailed string representation."""
        return (
            f"PlainDateTime({self._year}, {self._month}, {self._day}, "
            f"{self._hour}, {self._minute}, {self._second}, {self._microsecond})"
        )

    def __eq__(self, other) -> bool:
        """Check equality with another PlainDateTime."""
        if not isinstance(other, PlainDateTime):
            return False
        return (
            self._year == other._year
            and self._month == other._month
            and self._day == other._day
            and self._hour == other._hour
            and self._minute == other._minute
            and self._second == other._second
            and self._microsecond == other._microsecond
        )

    def __lt__(self, other) -> bool:
        """Check if this datetime is less than another."""
        if not isinstance(other, PlainDateTime):
            raise InvalidArgumentError("Expected PlainDateTime object")
        return (self._year, self._month, self._day, self._hour, self._minute, self._second, self._microsecond) < (
            other._year,
            other._month,
            other._day,
            other._hour,
            other._minute,
            other._second,
            other._microsecond,
        )

    def __le__(self, other) -> bool:
        """Check if this datetime is less than or equal to another."""
        return self == other or self < other

    def __gt__(self, other) -> bool:
        """Check if this datetime is greater than another."""
        return not self <= other

    def __ge__(self, other) -> bool:
        """Check if this datetime is greater than or equal to another."""
        return not self < other

    def __hash__(self) -> int:
        """Hash function for PlainDateTime."""
        return hash((self._year, self._month, self._day, self._hour, self._minute, self._second, self._microsecond))

    @classmethod
    def from_string(cls, datetime_string: str, calendar: Optional[Calendar] = None) -> "PlainDateTime":
        """Create PlainDateTime from ISO 8601 string."""
        year, month, day, hour, minute, second, microsecond = parse_iso_datetime(datetime_string)
        return cls(year, month, day, hour, minute, second, microsecond, calendar)

    @classmethod
    def now(cls, calendar: Optional[Calendar] = None) -> "PlainDateTime":
        """Get the current datetime."""
        now = datetime.now()
        return cls(now.year, now.month, now.day, now.hour, now.minute, now.second, now.microsecond, calendar)

    def until(self, other: "PlainDateTime") -> "Duration":
        """Calculate duration from this datetime to another.

        Args:
            other: The target datetime

        Returns:
            A Duration representing the difference
        """
        if not isinstance(other, PlainDateTime):
            raise InvalidArgumentError("Expected PlainDateTime")

        return other.subtract(self)  # type: ignore[return-value]

    def since(self, other: "PlainDateTime") -> "Duration":
        """Calculate duration from another datetime to this one.

        Args:
            other: The source datetime

        Returns:
            A Duration representing the difference
        """
        if not isinstance(other, PlainDateTime):
            raise InvalidArgumentError("Expected PlainDateTime")

        return self.subtract(other)  # type: ignore[return-value]

    def round(self, options: Union[str, dict]) -> "PlainDateTime":
        """Round the datetime to a specified increment.

        Args:
            options: Either a string unit name or dict with 'smallestUnit' and optional 'roundingIncrement'

        Returns:
            A new rounded PlainDateTime
        """
        if isinstance(options, str):
            smallest_unit = options
        elif isinstance(options, dict):
            smallest_unit = options.get("smallestUnit", "microseconds")
        else:
            raise InvalidArgumentError("Options must be string or dict")

        # For date units, delegate to PlainDate
        if smallest_unit in ["years", "months", "days"]:
            # For simplicity, we don't round date parts here
            return self

        # For time units, round the time part
        from .plain_time import PlainTime

        time_part = PlainTime(self._hour, self._minute, self._second, self._microsecond)
        rounded_time = time_part.round(options)

        new_datetime = PlainDateTime(
            self._year,
            self._month,
            self._day,
            rounded_time.hour,
            rounded_time.minute,
            rounded_time.second,
            rounded_time.microsecond,
            self._calendar,
        )

        # Handle case where rounding time caused day overflow
        if rounded_time.hour == 0 and self._hour == 23:
            # Time rounded to next day
            from .duration import Duration

            new_datetime = new_datetime.add(Duration(days=1))

        return new_datetime

    def with_plain_time(self, time: "PlainTime") -> "PlainDateTime":
        """Replace the time part with a new time.

        Args:
            time: The new time to use

        Returns:
            A new PlainDateTime with the new time
        """
        from .plain_time import PlainTime

        if not isinstance(time, PlainTime):
            raise InvalidArgumentError("Expected PlainTime")

        return PlainDateTime(
            self._year, self._month, self._day, time.hour, time.minute, time.second, time.microsecond, self._calendar
        )

    def with_calendar(self, calendar: Calendar) -> "PlainDateTime":
        """Replace the calendar with a new calendar.

        Args:
            calendar: The new calendar to use

        Returns:
            A new PlainDateTime with the new calendar
        """
        if not isinstance(calendar, Calendar):
            raise InvalidArgumentError("Expected Calendar")

        return PlainDateTime(
            self._year, self._month, self._day, self._hour, self._minute, self._second, self._microsecond, calendar
        )

    def equals(self, other: "PlainDateTime") -> bool:
        """Check if this datetime equals another.

        Args:
            other: The datetime to compare

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
    def compare(a: "PlainDateTime", b: "PlainDateTime") -> int:
        """Compare two PlainDateTime objects.

        Args:
            a: First PlainDateTime
            b: Second PlainDateTime

        Returns:
            -1 if a < b, 0 if a == b, 1 if a > b
        """
        if not isinstance(a, PlainDateTime) or not isinstance(b, PlainDateTime):
            raise InvalidArgumentError("Both arguments must be PlainDateTime")

        if a < b:
            return -1
        elif a > b:
            return 1
        else:
            return 0

    @classmethod
    def from_any(cls, value: Union[str, dict, "PlainDateTime"]) -> "PlainDateTime":
        """Create a PlainDateTime from various input types.

        Args:
            value: String, dict, or PlainDateTime

        Returns:
            A new PlainDateTime
        """
        if isinstance(value, PlainDateTime):
            return value
        elif isinstance(value, str):
            return cls.from_string(value)
        elif isinstance(value, dict):
            year = value.get("year")
            month = value.get("month")
            day = value.get("day")
            hour = value.get("hour", 0)
            minute = value.get("minute", 0)
            second = value.get("second", 0)
            microsecond = value.get("microsecond", 0)
            calendar = value.get("calendar")

            if year is None or month is None or day is None:
                raise InvalidArgumentError("year, month, and day are required")

            if calendar and isinstance(calendar, str):
                calendar = Calendar.from_string(calendar)

            return cls(year, month, day, hour, minute, second, microsecond, calendar)
        else:
            raise InvalidArgumentError(f"Cannot create PlainDateTime from {type(value)}")
