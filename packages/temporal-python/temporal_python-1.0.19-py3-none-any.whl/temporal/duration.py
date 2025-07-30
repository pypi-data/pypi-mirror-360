"""
Duration implementation for the Temporal API.
"""

import re
from typing import Optional, Union

from .exceptions import InvalidArgumentError, RangeError


class Duration:
    """Represents a duration of time."""

    def __init__(
        self,
        years: int = 0,
        months: int = 0,
        weeks: int = 0,
        days: int = 0,
        hours: int = 0,
        minutes: int = 0,
        seconds: int = 0,
        microseconds: int = 0,
    ):
        """Initialize a Duration with time components."""
        # Validate inputs
        for name, value in [
            ("years", years),
            ("months", months),
            ("weeks", weeks),
            ("days", days),
            ("hours", hours),
            ("minutes", minutes),
            ("seconds", seconds),
            ("microseconds", microseconds),
        ]:
            if not isinstance(value, (int, float)):
                raise InvalidArgumentError(f"{name} must be a number")
            # Warn about precision loss when converting floats to ints
            if isinstance(value, float) and value != int(value):
                import warnings

                warnings.warn(
                    f"Converting {name} from float {value} to int {int(value)} - precision may be lost",
                    UserWarning,
                    stacklevel=2,
                )

        self._years = int(years)
        self._months = int(months)
        self._weeks = int(weeks)
        self._days = int(days)
        self._hours = int(hours)
        self._minutes = int(minutes)
        self._seconds = int(seconds)
        self._microseconds = int(microseconds)

        # Normalize the duration
        self._normalize()

    def _normalize(self) -> None:
        """Normalize the duration components."""
        # Normalize microseconds to seconds
        if abs(self._microseconds) >= 1000000:
            extra_seconds = self._microseconds // 1000000
            self._seconds += extra_seconds
            self._microseconds -= extra_seconds * 1000000

        # Normalize seconds to minutes
        if abs(self._seconds) >= 60:
            extra_minutes = self._seconds // 60
            self._minutes += extra_minutes
            self._seconds -= extra_minutes * 60

        # Normalize minutes to hours
        if abs(self._minutes) >= 60:
            extra_hours = self._minutes // 60
            self._hours += extra_hours
            self._minutes -= extra_hours * 60

        # Normalize hours to days
        if abs(self._hours) >= 24:
            extra_days = self._hours // 24
            self._days += extra_days
            self._hours -= extra_days * 24

        # Normalize weeks to days
        if self._weeks != 0:
            self._days += self._weeks * 7
            self._weeks = 0

    @property
    def years(self) -> int:
        """Get the years component."""
        return self._years

    @property
    def months(self) -> int:
        """Get the months component."""
        return self._months

    @property
    def weeks(self) -> int:
        """Get the weeks component."""
        return self._weeks

    @property
    def days(self) -> int:
        """Get the days component."""
        return self._days

    @property
    def hours(self) -> int:
        """Get the hours component."""
        return self._hours

    @property
    def minutes(self) -> int:
        """Get the minutes component."""
        return self._minutes

    @property
    def seconds(self) -> int:
        """Get the seconds component."""
        return self._seconds

    @property
    def microseconds(self) -> int:
        """Get the microseconds component."""
        return self._microseconds

    def total_seconds(self) -> float:
        """Get the total duration in seconds (excluding years and months)."""
        return self._days * 24 * 3600 + self._hours * 3600 + self._minutes * 60 + self._seconds + self._microseconds / 1000000

    def add(self, other: "Duration") -> "Duration":
        """Add another duration to this one."""
        if not isinstance(other, Duration):
            raise InvalidArgumentError("Expected Duration object")

        return Duration(
            years=self._years + other._years,
            months=self._months + other._months,
            weeks=self._weeks + other._weeks,
            days=self._days + other._days,
            hours=self._hours + other._hours,
            minutes=self._minutes + other._minutes,
            seconds=self._seconds + other._seconds,
            microseconds=self._microseconds + other._microseconds,
        )

    def subtract(self, other: "Duration") -> "Duration":
        """Subtract another duration from this one."""
        if not isinstance(other, Duration):
            raise InvalidArgumentError("Expected Duration object")

        return Duration(
            years=self._years - other._years,
            months=self._months - other._months,
            weeks=self._weeks - other._weeks,
            days=self._days - other._days,
            hours=self._hours - other._hours,
            minutes=self._minutes - other._minutes,
            seconds=self._seconds - other._seconds,
            microseconds=self._microseconds - other._microseconds,
        )

    def negated(self) -> "Duration":
        """Return a negated copy of this duration."""
        return Duration(
            years=-self._years,
            months=-self._months,
            weeks=-self._weeks,
            days=-self._days,
            hours=-self._hours,
            minutes=-self._minutes,
            seconds=-self._seconds,
            microseconds=-self._microseconds,
        )

    def abs(self) -> "Duration":
        """Return an absolute (positive) copy of this duration."""
        return Duration(
            years=abs(self._years),
            months=abs(self._months),
            weeks=abs(self._weeks),
            days=abs(self._days),
            hours=abs(self._hours),
            minutes=abs(self._minutes),
            seconds=abs(self._seconds),
            microseconds=abs(self._microseconds),
        )

    def with_fields(
        self,
        *,
        years: Optional[int] = None,
        months: Optional[int] = None,
        weeks: Optional[int] = None,
        days: Optional[int] = None,
        hours: Optional[int] = None,
        minutes: Optional[int] = None,
        seconds: Optional[int] = None,
        microseconds: Optional[int] = None,
    ) -> "Duration":
        """Return a new Duration with specified fields replaced."""
        return Duration(
            years=years if years is not None else self._years,
            months=months if months is not None else self._months,
            weeks=weeks if weeks is not None else self._weeks,
            days=days if days is not None else self._days,
            hours=hours if hours is not None else self._hours,
            minutes=minutes if minutes is not None else self._minutes,
            seconds=seconds if seconds is not None else self._seconds,
            microseconds=microseconds if microseconds is not None else self._microseconds,
        )

    def _format_date_components(self) -> list:
        """Format date components for ISO 8601 string."""
        parts = []
        if self._years:
            parts.append(f"{self._years}Y")
        if self._months:
            parts.append(f"{self._months}M")
        if self._weeks:
            parts.append(f"{self._weeks}W")
        if self._days:
            parts.append(f"{self._days}D")
        return parts

    def _format_time_components(self) -> list:
        """Format time components for ISO 8601 string."""
        time_parts = []
        if self._hours:
            time_parts.append(f"{self._hours}H")
        if self._minutes:
            time_parts.append(f"{self._minutes}M")
        if self._seconds or self._microseconds:
            if self._microseconds:
                # Handle case where seconds is 0 but microseconds is not
                total_seconds = self._seconds + self._microseconds / 1000000
                seconds_str = f"{total_seconds:.6f}".rstrip("0").rstrip(".")
                time_parts.append(f"{seconds_str}S")
            else:
                time_parts.append(f"{self._seconds}S")
        return time_parts

    def __str__(self) -> str:
        """Return ISO 8601 duration string representation."""
        if self._is_zero():
            return "PT0S"

        parts = self._format_date_components()
        time_parts = self._format_time_components()

        result = "P" + "".join(parts)
        if time_parts:
            result += "T" + "".join(time_parts)

        return result

    def __repr__(self) -> str:
        """Return detailed string representation."""
        return (
            f"Duration(years={self._years}, months={self._months}, "
            f"weeks={self._weeks}, days={self._days}, hours={self._hours}, "
            f"minutes={self._minutes}, seconds={self._seconds}, "
            f"microseconds={self._microseconds})"
        )

    def __eq__(self, other: object) -> bool:
        """Check equality with another Duration."""
        if not isinstance(other, Duration):
            return False
        return (
            self._years == other._years
            and self._months == other._months
            and self._weeks == other._weeks
            and self._days == other._days
            and self._hours == other._hours
            and self._minutes == other._minutes
            and self._seconds == other._seconds
            and self._microseconds == other._microseconds
        )

    def __add__(self, other: "Duration") -> "Duration":
        """Add operator."""
        return self.add(other)

    def __sub__(self, other: "Duration") -> "Duration":
        """Subtract operator."""
        return self.subtract(other)

    def __neg__(self) -> "Duration":
        """Negation operator."""
        return self.negated()

    def __abs__(self) -> "Duration":
        """Absolute value operator."""
        return self.abs()

    def __hash__(self) -> int:
        """Hash function for Duration."""
        return hash(
            (self._years, self._months, self._weeks, self._days, self._hours, self._minutes, self._seconds, self._microseconds)
        )

    @property
    def sign(self) -> int:
        """Get the sign of the duration (-1, 0, or 1)."""
        non_zero_components = [
            self._years,
            self._months,
            self._weeks,
            self._days,
            self._hours,
            self._minutes,
            self._seconds,
            self._microseconds,
        ]

        # Check if all components are zero
        if all(x == 0 for x in non_zero_components):
            return 0

        # Check if any component is negative
        if any(x < 0 for x in non_zero_components):
            return -1

        # All components are positive
        return 1

    @property
    def blank(self) -> bool:
        """Check if this is a blank (zero) duration."""
        return self._is_zero()

    def _validate_total_unit(self, unit: str, relative_to: object) -> None:
        """Validate unit and relative_to parameters for total calculation."""
        if unit not in ["years", "months", "weeks", "days", "hours", "minutes", "seconds", "microseconds"]:
            raise InvalidArgumentError(f"Invalid unit: {unit}")

        # For years and months, we need a reference point
        if unit in ["years", "months"] and relative_to is None:
            raise InvalidArgumentError(f"relative_to is required for unit '{unit}'")

    def _calculate_time_unit_total(self, unit: str, total_seconds: float) -> float:
        """Calculate total for time-based units."""
        unit_conversions = {
            "microseconds": 1000000,
            "seconds": 1,
            "minutes": 1 / 60,
            "hours": 1 / 3600,
            "days": 1 / (24 * 3600),
            "weeks": 1 / (7 * 24 * 3600),
        }
        if unit in unit_conversions:
            return total_seconds * unit_conversions[unit]
        return 0.0

    def _calculate_calendar_unit_total(self, unit: str, total_seconds: float, relative_to: object) -> float:
        """Calculate total for calendar-based units (months, years)."""
        if unit == "months":
            # This is complex and depends on the reference date
            # For now, approximate as 30.44 days per month
            if relative_to:
                # Could implement proper calculation based on reference date
                pass
            return (total_seconds / (24 * 3600)) / 30.44 + self._months + self._years * 12
        elif unit == "years":
            # This is complex and depends on the reference date
            # For now, approximate as 365.25 days per year
            if relative_to:
                # Could implement proper calculation based on reference date
                pass
            return (total_seconds / (24 * 3600)) / 365.25 + self._years + self._months / 12
        return 0.0

    def total(self, unit: str, relative_to: object = None) -> float:
        """Calculate the total duration in the specified unit.

        Args:
            unit: The unit to calculate total in ('years', 'months', 'weeks', 'days', 'hours', 'minutes', 'seconds', 'microseconds')
            relative_to: Reference temporal object for calendar calculations (required for years/months)

        Returns:
            Total duration in the specified unit
        """
        self._validate_total_unit(unit, relative_to)

        # Convert everything to seconds first (excluding years/months)
        total_seconds = self.total_seconds()

        if unit in ["years", "months"]:
            return self._calculate_calendar_unit_total(unit, total_seconds, relative_to)
        else:
            return self._calculate_time_unit_total(unit, total_seconds)

    def _parse_round_options(self, options: Union[str, dict]) -> tuple:
        """Parse rounding options to extract smallest unit and increment."""
        if isinstance(options, str):
            return options, 1
        elif isinstance(options, dict):
            smallest_unit = options.get("smallestUnit", "microseconds")
            rounding_increment = options.get("roundingIncrement", 1)
            return smallest_unit, rounding_increment
        else:
            raise InvalidArgumentError("Options must be string or dict")

    def _round_to_years(self, rounding_increment: int) -> "Duration":
        """Round duration to years."""
        return Duration(years=round(self._years / rounding_increment) * rounding_increment)

    def _round_to_months(self, rounding_increment: int) -> "Duration":
        """Round duration to months."""
        return Duration(years=self._years, months=round(self._months / rounding_increment) * rounding_increment)

    def _round_to_weeks(self, rounding_increment: int) -> "Duration":
        """Round duration to weeks."""
        total_weeks = self._weeks + self._days / 7
        rounded_weeks = round(total_weeks / rounding_increment) * rounding_increment
        return Duration(years=self._years, months=self._months, weeks=rounded_weeks)

    def _round_to_days(self, rounding_increment: int) -> "Duration":
        """Round duration to days."""
        total_days = self._days + self._hours / 24
        rounded_days = round(total_days / rounding_increment) * rounding_increment
        return Duration(years=self._years, months=self._months, days=rounded_days)

    def _round_to_hours(self, rounding_increment: int) -> "Duration":
        """Round duration to hours."""
        total_hours = self._hours + self._minutes / 60
        rounded_hours = round(total_hours / rounding_increment) * rounding_increment
        return Duration(years=self._years, months=self._months, days=self._days, hours=rounded_hours)

    def _round_to_minutes(self, rounding_increment: int) -> "Duration":
        """Round duration to minutes."""
        total_minutes = self._minutes + self._seconds / 60
        rounded_minutes = round(total_minutes / rounding_increment) * rounding_increment
        return Duration(years=self._years, months=self._months, days=self._days, hours=self._hours, minutes=rounded_minutes)

    def _round_to_seconds(self, rounding_increment: int) -> "Duration":
        """Round duration to seconds."""
        total_seconds = self._seconds + self._microseconds / 1000000
        rounded_seconds = round(total_seconds / rounding_increment) * rounding_increment
        return Duration(
            years=self._years,
            months=self._months,
            days=self._days,
            hours=self._hours,
            minutes=self._minutes,
            seconds=rounded_seconds,
        )

    def _round_to_microseconds(self, rounding_increment: int) -> "Duration":
        """Round duration to microseconds."""
        rounded_microseconds = round(self._microseconds / rounding_increment) * rounding_increment
        return Duration(
            years=self._years,
            months=self._months,
            days=self._days,
            hours=self._hours,
            minutes=self._minutes,
            seconds=self._seconds,
            microseconds=rounded_microseconds,
        )

    def round(self, options: Union[str, dict]) -> "Duration":
        """Round the duration to a specified increment.

        Args:
            options: Either a string unit name or dict with 'smallestUnit' and optional 'roundingIncrement'

        Returns:
            A new rounded Duration
        """
        smallest_unit, rounding_increment = self._parse_round_options(options)

        # Route to appropriate rounding method
        round_methods = {
            "years": self._round_to_years,
            "months": self._round_to_months,
            "weeks": self._round_to_weeks,
            "days": self._round_to_days,
            "hours": self._round_to_hours,
            "minutes": self._round_to_minutes,
            "seconds": self._round_to_seconds,
            "microseconds": self._round_to_microseconds,
        }

        if smallest_unit in round_methods:
            return round_methods[smallest_unit](rounding_increment)
        # Fallback - return a copy
        return Duration(
            years=self._years,
            months=self._months,
            weeks=self._weeks,
            days=self._days,
            hours=self._hours,
            minutes=self._minutes,
            seconds=self._seconds,
            microseconds=self._microseconds,
        )

    def to_json(self) -> str:
        """Convert to JSON string."""
        return str(self)

    def to_locale_string(self, locale: str = "en-US") -> str:
        """Convert to locale-specific string representation."""
        # Basic implementation - could be enhanced with full locale support
        return str(self)

    def _is_zero(self) -> bool:
        """Check if this is a zero duration."""
        return all(
            getattr(self, f"_{field}") == 0
            for field in ["years", "months", "weeks", "days", "hours", "minutes", "seconds", "microseconds"]
        )

    @classmethod
    def from_string(cls, duration_string: str) -> "Duration":
        """Create Duration from ISO 8601 string."""
        # ISO 8601 duration pattern
        pattern = re.compile(
            r"^P(?:(\d+)Y)?(?:(\d+)M)?(?:(\d+)W)?(?:(\d+)D)?(?:T(?:(\d+)H)?(?:(\d+)M)?(?:(\d+(?:\.\d+)?)S)?)?$"
        )

        match = pattern.match(duration_string.upper())
        if not match:
            raise InvalidArgumentError(f"Invalid ISO 8601 duration format: {duration_string}")

        years, months, weeks, days, hours, minutes, seconds = match.groups()

        # Convert to integers/floats, defaulting to 0
        years = int(years) if years else 0
        months = int(months) if months else 0
        weeks = int(weeks) if weeks else 0
        days = int(days) if days else 0
        hours = int(hours) if hours else 0
        minutes = int(minutes) if minutes else 0

        # Handle fractional seconds
        if seconds:
            seconds_float = float(seconds)
            seconds_int = int(seconds_float)
            microseconds = int((seconds_float - seconds_int) * 1000000)
        else:
            seconds_int = 0
            microseconds = 0

        return cls(years, months, weeks, days, hours, minutes, seconds_int, microseconds)

    @staticmethod
    def compare(a: "Duration", b: "Duration") -> int:
        """Compare two Duration objects.

        Args:
            a: First Duration
            b: Second Duration

        Returns:
            -1 if a < b, 0 if a == b, 1 if a > b
        """
        if not isinstance(a, Duration) or not isinstance(b, Duration):
            raise InvalidArgumentError("Both arguments must be Duration")

        # Compare total seconds for time components
        a_seconds = a.total_seconds()
        b_seconds = b.total_seconds()

        # For years and months, we need to be careful as they're not directly comparable
        # We'll compare them separately
        a_months_total = a._years * 12 + a._months
        b_months_total = b._years * 12 + b._months

        if a_months_total != b_months_total:
            return -1 if a_months_total < b_months_total else 1

        if a_seconds < b_seconds:
            return -1
        elif a_seconds > b_seconds:
            return 1
        else:
            return 0

    @classmethod
    def from_any(cls, value: Union[str, dict, "Duration"]) -> "Duration":
        """Create a Duration from various input types.

        Args:
            value: String, dict, or Duration

        Returns:
            A new Duration
        """
        if isinstance(value, Duration):
            return value
        elif isinstance(value, str):
            return cls.from_string(value)
        elif isinstance(value, dict):
            return cls(**value)
        else:
            raise InvalidArgumentError(f"Cannot create Duration from {type(value)}")
