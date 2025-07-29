"""
Instant implementation for the Temporal API.
"""

from typing import Union, Optional
from datetime import datetime, timezone
from .duration import Duration
from .exceptions import InvalidArgumentError, RangeError


class Instant:
    """Represents an exact point in time."""
    
    def __init__(self, epoch_seconds: float):
        """Initialize an Instant with seconds since Unix epoch."""
        if not isinstance(epoch_seconds, (int, float)):
            raise InvalidArgumentError("epoch_seconds must be a number")
        
        self._epoch_seconds = float(epoch_seconds)
    
    @property
    def epoch_seconds(self) -> float:
        """Get seconds since Unix epoch."""
        return self._epoch_seconds
    
    @property
    def epoch_milliseconds(self) -> float:
        """Get milliseconds since Unix epoch."""
        return self._epoch_seconds * 1000
    
    @property
    def epoch_microseconds(self) -> float:
        """Get microseconds since Unix epoch."""
        return self._epoch_seconds * 1000000
    
    def add(self, duration: Duration) -> 'Instant':
        """Add a duration to this instant."""
        if not isinstance(duration, Duration):
            raise InvalidArgumentError("Expected Duration object")
        
        # Convert duration to seconds
        additional_seconds = duration.total_seconds()
        
        # Note: We ignore years and months for Instant arithmetic
        # as they are calendar-dependent
        if duration.years != 0 or duration.months != 0:
            raise InvalidArgumentError("Cannot add years or months to Instant")
        
        return Instant(self._epoch_seconds + additional_seconds)
    
    def subtract(self, other: Union['Instant', Duration]) -> Union['Instant', Duration]:
        """Subtract another instant or duration from this instant."""
        if isinstance(other, Duration):
            # Subtract duration - negate and add
            negated_duration = other.negated()
            return self.add(negated_duration)
        elif isinstance(other, Instant):
            # Subtract instant - return duration
            diff_seconds = self._epoch_seconds - other._epoch_seconds
            
            # Convert to duration components
            total_seconds = abs(diff_seconds)
            days = int(total_seconds // (24 * 3600))
            remaining_seconds = total_seconds % (24 * 3600)
            hours = int(remaining_seconds // 3600)
            remaining_seconds %= 3600
            minutes = int(remaining_seconds // 60)
            seconds = int(remaining_seconds % 60)
            microseconds = int((remaining_seconds % 1) * 1000000)
            
            if diff_seconds < 0:
                days, hours, minutes, seconds, microseconds = (
                    -days, -hours, -minutes, -seconds, -microseconds
                )
            
            return Duration(days=days, hours=hours, minutes=minutes, 
                          seconds=seconds, microseconds=microseconds)
        else:
            raise InvalidArgumentError("Expected Instant or Duration object")
    
    def to_zoned_date_time(self, timezone) -> 'ZonedDateTime':
        """Convert to ZonedDateTime in the given timezone."""
        from .timezone import TimeZone
        from .zoned_date_time import ZonedDateTime
        
        if not isinstance(timezone, TimeZone):
            raise InvalidArgumentError("Expected TimeZone object")
        
        # Create datetime in the specified timezone
        dt = datetime.fromtimestamp(self._epoch_seconds, tz=timezone.zone_info)
        
        return ZonedDateTime(
            dt.year, dt.month, dt.day,
            dt.hour, dt.minute, dt.second, dt.microsecond,
            timezone
        )
    
    def to_plain_date_time(self, timezone) -> 'PlainDateTime':
        """Convert to PlainDateTime in the given timezone."""
        zoned = self.to_zoned_date_time(timezone)
        return zoned.to_plain_date_time()
    
    def __str__(self) -> str:
        """Return ISO 8601 string representation."""
        dt = datetime.fromtimestamp(self._epoch_seconds, tz=timezone.utc)
        iso_string = dt.isoformat()
        # Ensure Z suffix for UTC
        if iso_string.endswith('+00:00'):
            iso_string = iso_string[:-6] + 'Z'
        return iso_string
    
    def __repr__(self) -> str:
        """Return detailed string representation."""
        return f"Instant({self._epoch_seconds})"
    
    def __eq__(self, other) -> bool:
        """Check equality with another Instant."""
        if not isinstance(other, Instant):
            return False
        # Use machine epsilon for better precision handling
        import sys
        epsilon = sys.float_info.epsilon * max(abs(self._epoch_seconds), abs(other._epoch_seconds), 1.0) * 10
        return abs(self._epoch_seconds - other._epoch_seconds) <= epsilon
    
    def __lt__(self, other) -> bool:
        """Check if this instant is less than another."""
        if not isinstance(other, Instant):
            raise InvalidArgumentError("Expected Instant object")
        return self._epoch_seconds < other._epoch_seconds
    
    def __le__(self, other) -> bool:
        """Check if this instant is less than or equal to another."""
        return self == other or self < other
    
    def __gt__(self, other) -> bool:
        """Check if this instant is greater than another."""
        return not self <= other
    
    def __ge__(self, other) -> bool:
        """Check if this instant is greater than or equal to another."""
        return not self < other
    
    def __hash__(self) -> int:
        """Hash function for Instant."""
        return hash(self._epoch_seconds)
    
    @classmethod
    def from_string(cls, instant_string: str) -> 'Instant':
        """Create Instant from ISO 8601 string."""
        try:
            # Parse ISO string
            if instant_string.endswith('Z'):
                dt = datetime.fromisoformat(instant_string[:-1] + '+00:00')
            else:
                dt = datetime.fromisoformat(instant_string)
            
            # Convert to UTC if timezone-aware
            if dt.tzinfo is not None:
                dt = dt.astimezone(timezone.utc)
            else:
                dt = dt.replace(tzinfo=timezone.utc)
            
            return cls(dt.timestamp())
        except (ValueError, TypeError, OverflowError) as e:
            raise InvalidArgumentError(f"Invalid ISO instant format: {instant_string}") from e
    
    @classmethod
    def now(cls) -> 'Instant':
        """Get the current instant."""
        return cls(datetime.now(timezone.utc).timestamp())
    
    @classmethod
    def from_epoch_seconds(cls, seconds: float) -> 'Instant':
        """Create Instant from epoch seconds."""
        return cls(seconds)
    
    @classmethod
    def from_epoch_milliseconds(cls, milliseconds: float) -> 'Instant':
        """Create Instant from epoch milliseconds."""
        return cls(milliseconds / 1000)
    
    @classmethod
    def from_epoch_microseconds(cls, microseconds: float) -> 'Instant':
        """Create Instant from epoch microseconds."""
        return cls(microseconds / 1000000)
