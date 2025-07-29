"""
PlainDateTime implementation for the Temporal API.
"""

from typing import Union, Optional
from datetime import datetime
from .utils import (validate_date_fields, validate_time_fields, parse_iso_datetime, 
                   pad_zero, format_microseconds)
from .calendar import Calendar
from .exceptions import InvalidArgumentError


class PlainDateTime:
    """Represents a date and time without time zone information."""
    
    def __init__(self, year: int, month: int, day: int, 
                 hour: int = 0, minute: int = 0, second: int = 0, microsecond: int = 0,
                 calendar: Optional[Calendar] = None):
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
    
    def to_plain_date(self) -> 'PlainDate':
        """Extract the date part."""
        from .plain_date import PlainDate
        return PlainDate(self._year, self._month, self._day, self._calendar)
    
    def to_plain_time(self) -> 'PlainTime':
        """Extract the time part."""
        from .plain_time import PlainTime
        return PlainTime(self._hour, self._minute, self._second, self._microsecond)
    
    def to_zoned_date_time(self, timezone) -> 'ZonedDateTime':
        """Convert to ZonedDateTime with the given timezone."""
        from .zoned_date_time import ZonedDateTime
        return ZonedDateTime(
            self._year, self._month, self._day,
            self._hour, self._minute, self._second, self._microsecond,
            timezone, self._calendar
        )
    
    def add(self, duration) -> 'PlainDateTime':
        """Add a duration to this datetime."""
        from .duration import Duration
        if not isinstance(duration, Duration):
            raise InvalidArgumentError("Expected Duration object")
        
        # Add date components
        date_part = self.to_plain_date().add(duration)
        
        # Add time components
        time_part = self.to_plain_time().add(duration)
        
        return PlainDateTime(
            date_part.year, date_part.month, date_part.day,
            time_part.hour, time_part.minute, time_part.second, time_part.microsecond,
            self._calendar
        )
    
    def subtract(self, other) -> Union['PlainDateTime', 'Duration']:
        """Subtract another datetime or duration from this datetime."""
        from .duration import Duration
        
        if isinstance(other, Duration):
            # Subtract duration - negate and add
            negated_duration = Duration(
                -other.years, -other.months, -other.weeks, -other.days,
                -other.hours, -other.minutes, -other.seconds, -other.microseconds
            )
            return self.add(negated_duration)
        elif isinstance(other, PlainDateTime):
            # Subtract datetime - return duration
            dt1 = datetime(self._year, self._month, self._day, 
                          self._hour, self._minute, self._second, self._microsecond)
            dt2 = datetime(other._year, other._month, other._day,
                          other._hour, other._minute, other._second, other._microsecond)
            delta = dt1 - dt2
            
            return Duration(
                days=delta.days,
                seconds=delta.seconds,
                microseconds=delta.microseconds
            )
        else:
            raise InvalidArgumentError("Expected PlainDateTime or Duration object")
    
    def with_fields(self, *, year: Optional[int] = None, month: Optional[int] = None,
                   day: Optional[int] = None, hour: Optional[int] = None,
                   minute: Optional[int] = None, second: Optional[int] = None,
                   microsecond: Optional[int] = None, calendar: Optional[Calendar] = None) -> 'PlainDateTime':
        """Return a new PlainDateTime with specified fields replaced."""
        new_year = year if year is not None else self._year
        new_month = month if month is not None else self._month
        new_day = day if day is not None else self._day
        new_hour = hour if hour is not None else self._hour
        new_minute = minute if minute is not None else self._minute
        new_second = second if second is not None else self._second
        new_microsecond = microsecond if microsecond is not None else self._microsecond
        new_calendar = calendar if calendar is not None else self._calendar
        
        return PlainDateTime(new_year, new_month, new_day, new_hour, new_minute, 
                           new_second, new_microsecond, new_calendar)
    
    def __str__(self) -> str:
        """Return ISO 8601 string representation."""
        date_str = f"{self._year:04d}-{pad_zero(self._month)}-{pad_zero(self._day)}"
        time_str = f"{pad_zero(self._hour)}:{pad_zero(self._minute)}:{pad_zero(self._second)}"
        if self._microsecond:
            time_str += format_microseconds(self._microsecond)
        return f"{date_str}T{time_str}"
    
    def __repr__(self) -> str:
        """Return detailed string representation."""
        return (f"PlainDateTime({self._year}, {self._month}, {self._day}, "
                f"{self._hour}, {self._minute}, {self._second}, {self._microsecond})")
    
    def __eq__(self, other) -> bool:
        """Check equality with another PlainDateTime."""
        if not isinstance(other, PlainDateTime):
            return False
        return (self._year == other._year and self._month == other._month and
                self._day == other._day and self._hour == other._hour and
                self._minute == other._minute and self._second == other._second and
                self._microsecond == other._microsecond)
    
    def __lt__(self, other) -> bool:
        """Check if this datetime is less than another."""
        if not isinstance(other, PlainDateTime):
            raise InvalidArgumentError("Expected PlainDateTime object")
        return ((self._year, self._month, self._day, self._hour, self._minute, 
                self._second, self._microsecond) < 
                (other._year, other._month, other._day, other._hour, other._minute,
                 other._second, other._microsecond))
    
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
        return hash((self._year, self._month, self._day, self._hour, 
                    self._minute, self._second, self._microsecond))
    
    @classmethod
    def from_string(cls, datetime_string: str, calendar: Optional[Calendar] = None) -> 'PlainDateTime':
        """Create PlainDateTime from ISO 8601 string."""
        year, month, day, hour, minute, second, microsecond = parse_iso_datetime(datetime_string)
        return cls(year, month, day, hour, minute, second, microsecond, calendar)
    
    @classmethod
    def now(cls, calendar: Optional[Calendar] = None) -> 'PlainDateTime':
        """Get the current datetime."""
        now = datetime.now()
        return cls(now.year, now.month, now.day, now.hour, now.minute, 
                  now.second, now.microsecond, calendar)
