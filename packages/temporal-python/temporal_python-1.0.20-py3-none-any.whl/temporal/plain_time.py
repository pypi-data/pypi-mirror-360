"""
PlainTime implementation for the Temporal API.
"""

from typing import TYPE_CHECKING, Optional, Union

from .exceptions import InvalidArgumentError, RangeError
from .utils import format_microseconds, pad_zero, parse_iso_time, validate_time_fields

if TYPE_CHECKING:
    from .duration import Duration


class PlainTime:
    """Represents a time without date or time zone information."""

    def __init__(self, hour: int = 0, minute: int = 0, second: int = 0, microsecond: int = 0):
        """Initialize a PlainTime with hour, minute, second, and microsecond."""
        validate_time_fields(hour, minute, second, microsecond)

        self._hour = hour
        self._minute = minute
        self._second = second
        self._microsecond = microsecond

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

    def add(self, duration) -> "PlainTime":
        """Add a duration to this time."""
        from .duration import Duration

        if not isinstance(duration, Duration):
            raise InvalidArgumentError("Expected Duration object")

        # Convert everything to microseconds for calculation
        total_microseconds = (
            self._hour * 3600 * 1000000
            + self._minute * 60 * 1000000
            + self._second * 1000000
            + self._microsecond
            + duration.hours * 3600 * 1000000
            + duration.minutes * 60 * 1000000
            + duration.seconds * 1000000
            + duration.microseconds
        )

        # Handle day overflow/underflow by taking modulo
        total_microseconds = total_microseconds % (24 * 3600 * 1000000)
        if total_microseconds < 0:
            total_microseconds += 24 * 3600 * 1000000

        # Convert back to time components
        total_seconds, microsecond = divmod(total_microseconds, 1000000)
        total_minutes, second = divmod(total_seconds, 60)
        hour, minute = divmod(total_minutes, 60)

        return PlainTime(int(hour), int(minute), int(second), int(microsecond))

    def subtract(self, other) -> Union["PlainTime", "Duration"]:
        """Subtract another time or duration from this time."""
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
        elif isinstance(other, PlainTime):
            # Subtract time - return duration
            self_microseconds = (
                self._hour * 3600 * 1000000 + self._minute * 60 * 1000000 + self._second * 1000000 + self._microsecond
            )
            other_microseconds = (
                other._hour * 3600 * 1000000 + other._minute * 60 * 1000000 + other._second * 1000000 + other._microsecond
            )

            diff_microseconds = self_microseconds - other_microseconds

            # Convert to duration components
            total_seconds, microseconds = divmod(abs(diff_microseconds), 1000000)
            minutes, seconds = divmod(total_seconds, 60)
            hours, minutes = divmod(minutes, 60)

            if diff_microseconds < 0:
                hours, minutes, seconds, microseconds = -hours, -minutes, -seconds, -microseconds

            return Duration(hours=int(hours), minutes=int(minutes), seconds=int(seconds), microseconds=int(microseconds))
        else:
            raise InvalidArgumentError("Expected PlainTime or Duration object")

    def with_fields(
        self,
        *,
        hour: Optional[int] = None,
        minute: Optional[int] = None,
        second: Optional[int] = None,
        microsecond: Optional[int] = None,
    ) -> "PlainTime":
        """Return a new PlainTime with specified fields replaced."""
        new_hour = hour if hour is not None else self._hour
        new_minute = minute if minute is not None else self._minute
        new_second = second if second is not None else self._second
        new_microsecond = microsecond if microsecond is not None else self._microsecond

        return PlainTime(new_hour, new_minute, new_second, new_microsecond)

    def __str__(self) -> str:
        """Return ISO 8601 string representation."""
        base = f"{pad_zero(self._hour)}:{pad_zero(self._minute)}:{pad_zero(self._second)}"
        if self._microsecond:
            base += format_microseconds(self._microsecond)
        return base

    def __repr__(self) -> str:
        """Return detailed string representation."""
        return f"PlainTime({self._hour}, {self._minute}, {self._second}, {self._microsecond})"

    def __eq__(self, other) -> bool:
        """Check equality with another PlainTime."""
        if not isinstance(other, PlainTime):
            return False
        return (
            self._hour == other._hour
            and self._minute == other._minute
            and self._second == other._second
            and self._microsecond == other._microsecond
        )

    def __lt__(self, other) -> bool:
        """Check if this time is less than another."""
        if not isinstance(other, PlainTime):
            raise InvalidArgumentError("Expected PlainTime object")
        return (self._hour, self._minute, self._second, self._microsecond) < (
            other._hour,
            other._minute,
            other._second,
            other._microsecond,
        )

    def __le__(self, other) -> bool:
        """Check if this time is less than or equal to another."""
        return self == other or self < other

    def __gt__(self, other) -> bool:
        """Check if this time is greater than another."""
        return not self <= other

    def __ge__(self, other) -> bool:
        """Check if this time is greater than or equal to another."""
        return not self < other

    def __hash__(self) -> int:
        """Hash function for PlainTime."""
        return hash((self._hour, self._minute, self._second, self._microsecond))

    @classmethod
    def from_string(cls, time_string: str) -> "PlainTime":
        """Create PlainTime from ISO 8601 string."""
        hour, minute, second, microsecond = parse_iso_time(time_string)
        return cls(hour, minute, second, microsecond)

    def until(self, other: "PlainTime") -> "Duration":
        """Calculate duration from this time to another.

        Args:
            other: The target time

        Returns:
            A Duration representing the difference
        """
        if not isinstance(other, PlainTime):
            raise InvalidArgumentError("Expected PlainTime")

        return other.subtract(self)  # type: ignore[return-value]

    def since(self, other: "PlainTime") -> "Duration":
        """Calculate duration from another time to this one.

        Args:
            other: The source time

        Returns:
            A Duration representing the difference
        """
        if not isinstance(other, PlainTime):
            raise InvalidArgumentError("Expected PlainTime")

        return self.subtract(other)  # type: ignore[return-value]

    def round(self, options: Union[str, dict]) -> "PlainTime":
        """Round the time to a specified increment.

        Args:
            options: Either a string unit name or dict with 'smallestUnit' and optional 'roundingIncrement'

        Returns:
            A new rounded PlainTime
        """
        if isinstance(options, str):
            smallest_unit = options
            rounding_increment = 1
        elif isinstance(options, dict):
            smallest_unit = options.get("smallestUnit", "microseconds")
            rounding_increment = options.get("roundingIncrement", 1)
        else:
            raise InvalidArgumentError("Options must be string or dict")

        # Convert to total microseconds
        total_microseconds = (
            self._hour * 3600 * 1000000 + self._minute * 60 * 1000000 + self._second * 1000000 + self._microsecond
        )

        if smallest_unit == "hours":
            increment_us = rounding_increment * 3600 * 1000000
        elif smallest_unit == "minutes":
            increment_us = rounding_increment * 60 * 1000000
        elif smallest_unit == "seconds":
            increment_us = rounding_increment * 1000000
        elif smallest_unit == "milliseconds":
            increment_us = rounding_increment * 1000
        elif smallest_unit == "microseconds":
            increment_us = rounding_increment
        else:
            raise InvalidArgumentError(f"Invalid unit: {smallest_unit}")

        # Round to the nearest increment
        rounded_us = round(total_microseconds / increment_us) * increment_us

        # Convert back to time components
        total_seconds, microsecond = divmod(rounded_us, 1000000)
        total_minutes, second = divmod(total_seconds, 60)
        hour, minute = divmod(total_minutes, 60)

        # Handle 24-hour wraparound
        hour = hour % 24

        return PlainTime(int(hour), int(minute), int(second), int(microsecond))

    def equals(self, other: "PlainTime") -> bool:
        """Check if this time equals another.

        Args:
            other: The time to compare

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
    def compare(a: "PlainTime", b: "PlainTime") -> int:
        """Compare two PlainTime objects.

        Args:
            a: First PlainTime
            b: Second PlainTime

        Returns:
            -1 if a < b, 0 if a == b, 1 if a > b
        """
        if not isinstance(a, PlainTime) or not isinstance(b, PlainTime):
            raise InvalidArgumentError("Both arguments must be PlainTime")

        if a < b:
            return -1
        elif a > b:
            return 1
        else:
            return 0

    @classmethod
    def from_any(cls, value: Union[str, dict, "PlainTime"]) -> "PlainTime":
        """Create a PlainTime from various input types.

        Args:
            value: String, dict, or PlainTime

        Returns:
            A new PlainTime
        """
        if isinstance(value, PlainTime):
            return value
        elif isinstance(value, str):
            return cls.from_string(value)
        elif isinstance(value, dict):
            hour = value.get("hour", 0)
            minute = value.get("minute", 0)
            second = value.get("second", 0)
            microsecond = value.get("microsecond", 0)

            return cls(hour, minute, second, microsecond)
        else:
            raise InvalidArgumentError(f"Cannot create PlainTime from {type(value)}")
