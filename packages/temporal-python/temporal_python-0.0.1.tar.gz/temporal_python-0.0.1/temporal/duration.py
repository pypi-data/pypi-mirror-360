"""
Duration implementation for the Temporal API.
"""

from typing import Union, Optional
import re
from .exceptions import InvalidArgumentError, RangeError


class Duration:
    """Represents a duration of time."""
    
    def __init__(self, years: int = 0, months: int = 0, weeks: int = 0, days: int = 0,
                 hours: int = 0, minutes: int = 0, seconds: int = 0, microseconds: int = 0):
        """Initialize a Duration with time components."""
        # Validate inputs
        for name, value in [('years', years), ('months', months), ('weeks', weeks), 
                           ('days', days), ('hours', hours), ('minutes', minutes), 
                           ('seconds', seconds), ('microseconds', microseconds)]:
            if not isinstance(value, (int, float)):
                raise InvalidArgumentError(f"{name} must be a number")
            # Warn about precision loss when converting floats to ints
            if isinstance(value, float) and value != int(value):
                import warnings
                warnings.warn(f"Converting {name} from float {value} to int {int(value)} - precision may be lost", 
                             UserWarning, stacklevel=2)
        
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
        return (self._days * 24 * 3600 + 
                self._hours * 3600 + 
                self._minutes * 60 + 
                self._seconds + 
                self._microseconds / 1000000)
    
    def add(self, other: 'Duration') -> 'Duration':
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
            microseconds=self._microseconds + other._microseconds
        )
    
    def subtract(self, other: 'Duration') -> 'Duration':
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
            microseconds=self._microseconds - other._microseconds
        )
    
    def negated(self) -> 'Duration':
        """Return a negated copy of this duration."""
        return Duration(
            years=-self._years,
            months=-self._months,
            weeks=-self._weeks,
            days=-self._days,
            hours=-self._hours,
            minutes=-self._minutes,
            seconds=-self._seconds,
            microseconds=-self._microseconds
        )
    
    def abs(self) -> 'Duration':
        """Return an absolute (positive) copy of this duration."""
        return Duration(
            years=abs(self._years),
            months=abs(self._months),
            weeks=abs(self._weeks),
            days=abs(self._days),
            hours=abs(self._hours),
            minutes=abs(self._minutes),
            seconds=abs(self._seconds),
            microseconds=abs(self._microseconds)
        )
    
    def with_fields(self, *, years: Optional[int] = None, months: Optional[int] = None,
                   weeks: Optional[int] = None, days: Optional[int] = None,
                   hours: Optional[int] = None, minutes: Optional[int] = None,
                   seconds: Optional[int] = None, microseconds: Optional[int] = None) -> 'Duration':
        """Return a new Duration with specified fields replaced."""
        return Duration(
            years=years if years is not None else self._years,
            months=months if months is not None else self._months,
            weeks=weeks if weeks is not None else self._weeks,
            days=days if days is not None else self._days,
            hours=hours if hours is not None else self._hours,
            minutes=minutes if minutes is not None else self._minutes,
            seconds=seconds if seconds is not None else self._seconds,
            microseconds=microseconds if microseconds is not None else self._microseconds
        )
    
    def __str__(self) -> str:
        """Return ISO 8601 duration string representation."""
        if self._is_zero():
            return "PT0S"
        
        parts = []
        
        # Date part
        if self._years:
            parts.append(f"{self._years}Y")
        if self._months:
            parts.append(f"{self._months}M")
        if self._weeks:
            parts.append(f"{self._weeks}W")
        if self._days:
            parts.append(f"{self._days}D")
        
        # Time part
        time_parts = []
        if self._hours:
            time_parts.append(f"{self._hours}H")
        if self._minutes:
            time_parts.append(f"{self._minutes}M")
        if self._seconds or self._microseconds:
            if self._microseconds:
                # Handle case where seconds is 0 but microseconds is not
                total_seconds = self._seconds + self._microseconds / 1000000
                seconds_str = f"{total_seconds:.6f}".rstrip('0').rstrip('.')
                time_parts.append(f"{seconds_str}S")
            else:
                time_parts.append(f"{self._seconds}S")
        
        result = "P" + "".join(parts)
        if time_parts:
            result += "T" + "".join(time_parts)
        
        return result
    
    def __repr__(self) -> str:
        """Return detailed string representation."""
        return (f"Duration(years={self._years}, months={self._months}, "
                f"weeks={self._weeks}, days={self._days}, hours={self._hours}, "
                f"minutes={self._minutes}, seconds={self._seconds}, "
                f"microseconds={self._microseconds})")
    
    def __eq__(self, other) -> bool:
        """Check equality with another Duration."""
        if not isinstance(other, Duration):
            return False
        return (self._years == other._years and self._months == other._months and
                self._weeks == other._weeks and self._days == other._days and
                self._hours == other._hours and self._minutes == other._minutes and
                self._seconds == other._seconds and self._microseconds == other._microseconds)
    
    def __add__(self, other) -> 'Duration':
        """Add operator."""
        return self.add(other)
    
    def __sub__(self, other) -> 'Duration':
        """Subtract operator."""
        return self.subtract(other)
    
    def __neg__(self) -> 'Duration':
        """Negation operator."""
        return self.negated()
    
    def __abs__(self) -> 'Duration':
        """Absolute value operator."""
        return self.abs()
    
    def __hash__(self) -> int:
        """Hash function for Duration."""
        return hash((self._years, self._months, self._weeks, self._days,
                    self._hours, self._minutes, self._seconds, self._microseconds))
    
    def _is_zero(self) -> bool:
        """Check if this is a zero duration."""
        return all(getattr(self, f'_{field}') == 0 for field in 
                   ['years', 'months', 'weeks', 'days', 'hours', 'minutes', 'seconds', 'microseconds'])
    
    @classmethod
    def from_string(cls, duration_string: str) -> 'Duration':
        """Create Duration from ISO 8601 string."""
        # ISO 8601 duration pattern
        pattern = re.compile(
            r'^P(?:(\d+)Y)?(?:(\d+)M)?(?:(\d+)W)?(?:(\d+)D)?(?:T(?:(\d+)H)?(?:(\d+)M)?(?:(\d+(?:\.\d+)?)S)?)?$'
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
