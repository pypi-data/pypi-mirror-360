"""
PlainDate implementation for the Temporal API.
"""

from typing import Union, Optional
from datetime import date
from .utils import validate_date_fields, parse_iso_date, pad_zero, get_days_in_month
from .calendar import Calendar
from .exceptions import InvalidArgumentError, RangeError


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
    
    def add(self, duration) -> 'PlainDate':
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
    
    def subtract(self, other) -> Union['PlainDate', 'Duration']:
        """Subtract another date or duration from this date."""
        from .duration import Duration
        
        if isinstance(other, Duration):
            # Subtract duration - negate and add
            negated_duration = Duration(
                -other.years, -other.months, -other.weeks, -other.days,
                -other.hours, -other.minutes, -other.seconds, -other.microseconds
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
    
    def with_fields(self, *, year: Optional[int] = None, month: Optional[int] = None, 
                   day: Optional[int] = None, calendar: Optional[Calendar] = None) -> 'PlainDate':
        """Return a new PlainDate with specified fields replaced."""
        new_year = year if year is not None else self._year
        new_month = month if month is not None else self._month
        new_day = day if day is not None else self._day
        new_calendar = calendar if calendar is not None else self._calendar
        
        return PlainDate(new_year, new_month, new_day, new_calendar)
    
    def to_plain_datetime(self, time=None) -> 'PlainDateTime':
        """Convert to PlainDateTime by adding time."""
        from .plain_time import PlainTime
        from .plain_date_time import PlainDateTime
        
        if time is None:
            time = PlainTime(0, 0, 0)
        elif not isinstance(time, PlainTime):
            raise InvalidArgumentError("Expected PlainTime object")
        
        return PlainDateTime(
            self._year, self._month, self._day,
            time.hour, time.minute, time.second, time.microsecond,
            self._calendar
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
        return (self._year == other._year and 
                self._month == other._month and 
                self._day == other._day)
    
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
    def from_string(cls, date_string: str, calendar: Optional[Calendar] = None) -> 'PlainDate':
        """Create PlainDate from ISO 8601 string."""
        year, month, day = parse_iso_date(date_string)
        return cls(year, month, day, calendar)
    
    @classmethod
    def today(cls, calendar: Optional[Calendar] = None) -> 'PlainDate':
        """Get today's date."""
        today = date.today()
        return cls(today.year, today.month, today.day, calendar)
