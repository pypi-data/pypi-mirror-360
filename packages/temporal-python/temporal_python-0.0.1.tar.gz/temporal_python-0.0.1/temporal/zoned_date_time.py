"""
ZonedDateTime implementation for the Temporal API.
"""

from typing import Union, Optional
from datetime import datetime
from .utils import validate_date_fields, validate_time_fields, pad_zero, format_microseconds
from .calendar import Calendar
from .timezone import TimeZone
from .exceptions import InvalidArgumentError


class ZonedDateTime:
    """Represents a date and time with time zone information."""
    
    def __init__(self, year: int, month: int, day: int,
                 hour: int = 0, minute: int = 0, second: int = 0, microsecond: int = 0,
                 timezone: Optional[TimeZone] = None, calendar: Optional[Calendar] = None):
        """Initialize a ZonedDateTime with date, time, and timezone components."""
        validate_date_fields(year, month, day)
        validate_time_fields(hour, minute, second, microsecond)
        
        if timezone is None:
            raise InvalidArgumentError("TimeZone is required")
        if not isinstance(timezone, TimeZone):
            raise InvalidArgumentError("Expected TimeZone object")
        
        self._year = year
        self._month = month
        self._day = day
        self._hour = hour
        self._minute = minute
        self._second = second
        self._microsecond = microsecond
        self._timezone = timezone
        self._calendar = calendar or Calendar()
        
        # Validate the datetime exists in the timezone
        try:
            self._datetime = datetime(year, month, day, hour, minute, second, microsecond,
                                    tzinfo=timezone.zone_info)
        except Exception as e:
            raise InvalidArgumentError(f"Invalid datetime for timezone: {e}")
    
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
    def timezone(self) -> TimeZone:
        """Get the timezone."""
        return self._timezone
    
    @property
    def calendar(self) -> Calendar:
        """Get the calendar."""
        return self._calendar
    
    @property
    def offset_seconds(self) -> int:
        """Get the UTC offset in seconds."""
        return int(self._datetime.utcoffset().total_seconds())
    
    @property
    def offset_string(self) -> str:
        """Get the UTC offset as a string (e.g., '+05:00')."""
        offset = self._datetime.utcoffset()
        total_seconds = int(offset.total_seconds())
        
        if total_seconds == 0:
            return 'Z'
        
        sign = '+' if total_seconds >= 0 else '-'
        abs_seconds = abs(total_seconds)
        hours, remainder = divmod(abs_seconds, 3600)
        minutes = remainder // 60
        
        return f"{sign}{hours:02d}:{minutes:02d}"
    
    def to_instant(self) -> 'Instant':
        """Convert to Instant."""
        from .instant import Instant
        return Instant(self._datetime.timestamp())
    
    def to_plain_date_time(self) -> 'PlainDateTime':
        """Convert to PlainDateTime by removing timezone information."""
        from .plain_date_time import PlainDateTime
        return PlainDateTime(
            self._year, self._month, self._day,
            self._hour, self._minute, self._second, self._microsecond,
            self._calendar
        )
    
    def to_plain_date(self) -> 'PlainDate':
        """Extract the date part."""
        from .plain_date import PlainDate
        return PlainDate(self._year, self._month, self._day, self._calendar)
    
    def to_plain_time(self) -> 'PlainTime':
        """Extract the time part."""
        from .plain_time import PlainTime
        return PlainTime(self._hour, self._minute, self._second, self._microsecond)
    
    def with_timezone(self, timezone: TimeZone) -> 'ZonedDateTime':
        """Convert to the same instant in a different timezone."""
        if not isinstance(timezone, TimeZone):
            raise InvalidArgumentError("Expected TimeZone object")
        
        # Convert to the new timezone
        new_dt = self._datetime.astimezone(timezone.zone_info)
        
        return ZonedDateTime(
            new_dt.year, new_dt.month, new_dt.day,
            new_dt.hour, new_dt.minute, new_dt.second, new_dt.microsecond,
            timezone, self._calendar
        )
    
    def add(self, duration) -> 'ZonedDateTime':
        """Add a duration to this zoned datetime."""
        from .duration import Duration
        if not isinstance(duration, Duration):
            raise InvalidArgumentError("Expected Duration object")
        
        # Convert to instant, add duration, convert back
        instant = self.to_instant()
        new_instant = instant.add(duration)
        return new_instant.to_zoned_date_time(self._timezone)
    
    def subtract(self, other) -> Union['ZonedDateTime', 'Duration']:
        """Subtract another zoned datetime or duration from this one."""
        from .duration import Duration
        
        if isinstance(other, Duration):
            # Subtract duration - negate and add
            negated_duration = other.negated()
            return self.add(negated_duration)
        elif isinstance(other, ZonedDateTime):
            # Subtract zoned datetime - return duration
            instant1 = self.to_instant()
            instant2 = other.to_instant()
            return instant1.subtract(instant2)
        else:
            raise InvalidArgumentError("Expected ZonedDateTime or Duration object")
    
    def with_fields(self, *, year: Optional[int] = None, month: Optional[int] = None,
                   day: Optional[int] = None, hour: Optional[int] = None,
                   minute: Optional[int] = None, second: Optional[int] = None,
                   microsecond: Optional[int] = None, timezone: Optional[TimeZone] = None,
                   calendar: Optional[Calendar] = None) -> 'ZonedDateTime':
        """Return a new ZonedDateTime with specified fields replaced."""
        new_year = year if year is not None else self._year
        new_month = month if month is not None else self._month
        new_day = day if day is not None else self._day
        new_hour = hour if hour is not None else self._hour
        new_minute = minute if minute is not None else self._minute
        new_second = second if second is not None else self._second
        new_microsecond = microsecond if microsecond is not None else self._microsecond
        new_timezone = timezone if timezone is not None else self._timezone
        new_calendar = calendar if calendar is not None else self._calendar
        
        return ZonedDateTime(new_year, new_month, new_day, new_hour, new_minute,
                           new_second, new_microsecond, new_timezone, new_calendar)
    
    def __str__(self) -> str:
        """Return ISO 8601 string representation with timezone."""
        date_str = f"{self._year:04d}-{pad_zero(self._month)}-{pad_zero(self._day)}"
        time_str = f"{pad_zero(self._hour)}:{pad_zero(self._minute)}:{pad_zero(self._second)}"
        if self._microsecond:
            time_str += format_microseconds(self._microsecond)
        
        return f"{date_str}T{time_str}{self.offset_string}"
    
    def __repr__(self) -> str:
        """Return detailed string representation."""
        return (f"ZonedDateTime({self._year}, {self._month}, {self._day}, "
                f"{self._hour}, {self._minute}, {self._second}, {self._microsecond}, "
                f"TimeZone('{self._timezone.id}'))")
    
    def __eq__(self, other) -> bool:
        """Check equality with another ZonedDateTime."""
        if not isinstance(other, ZonedDateTime):
            return False
        
        # Compare instants for equality
        return self.to_instant() == other.to_instant()
    
    def __lt__(self, other) -> bool:
        """Check if this zoned datetime is less than another."""
        if not isinstance(other, ZonedDateTime):
            raise InvalidArgumentError("Expected ZonedDateTime object")
        
        return self.to_instant() < other.to_instant()
    
    def __le__(self, other) -> bool:
        """Check if this zoned datetime is less than or equal to another."""
        return self == other or self < other
    
    def __gt__(self, other) -> bool:
        """Check if this zoned datetime is greater than another."""
        return not self <= other
    
    def __ge__(self, other) -> bool:
        """Check if this zoned datetime is greater than or equal to another."""
        return not self < other
    
    def __hash__(self) -> int:
        """Hash function for ZonedDateTime."""
        return hash(self.to_instant().epoch_seconds)
    
    @classmethod
    def from_string(cls, datetime_string: str, timezone: Optional[TimeZone] = None,
                   calendar: Optional[Calendar] = None) -> 'ZonedDateTime':
        """Create ZonedDateTime from ISO 8601 string with timezone."""
        try:
            # Parse the datetime string
            dt = datetime.fromisoformat(datetime_string)
            
            # If no timezone in string and none provided, raise error
            if dt.tzinfo is None and timezone is None:
                raise InvalidArgumentError("Timezone is required")
            
            # Use provided timezone if datetime has no timezone info
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.zone_info)
            elif timezone is not None:
                # Convert to the specified timezone
                dt = dt.astimezone(timezone.zone_info)
                timezone = TimeZone(str(dt.tzinfo))
            else:
                # Create TimeZone from the datetime's timezone
                timezone = TimeZone(str(dt.tzinfo))
            
            return cls(dt.year, dt.month, dt.day, dt.hour, dt.minute,
                      dt.second, dt.microsecond, timezone, calendar)
        except Exception as e:
            raise InvalidArgumentError(f"Invalid ISO zoned datetime format: {datetime_string}") from e
    
    @classmethod
    def now(cls, timezone: TimeZone, calendar: Optional[Calendar] = None) -> 'ZonedDateTime':
        """Get the current zoned datetime."""
        if not isinstance(timezone, TimeZone):
            raise InvalidArgumentError("Expected TimeZone object")
        
        now = datetime.now(timezone.zone_info)
        return cls(now.year, now.month, now.day, now.hour, now.minute,
                  now.second, now.microsecond, timezone, calendar)
