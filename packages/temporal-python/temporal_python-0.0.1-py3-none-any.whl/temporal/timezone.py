"""
TimeZone implementation for the Temporal API.
"""

import sys
from typing import Optional, Union
from .exceptions import InvalidArgumentError

# Import zoneinfo for Python 3.9+, fallback to backports.zoneinfo for older versions
try:
    from zoneinfo import ZoneInfo
except ImportError:
    try:
        from backports.zoneinfo import ZoneInfo
    except ImportError:
        raise ImportError("zoneinfo is required. Install backports.zoneinfo for Python < 3.9")


class TimeZone:
    """Represents a time zone."""
    
    def __init__(self, identifier: str):
        """Initialize a TimeZone with the given identifier."""
        try:
            self._zone_info = ZoneInfo(identifier)
            self._identifier = identifier
        except Exception as e:
            raise InvalidArgumentError(f"Invalid timezone identifier: {identifier}") from e
    
    @property
    def id(self) -> str:
        """Get the timezone identifier."""
        return self._identifier
    
    def __str__(self) -> str:
        """String representation of the timezone."""
        return self._identifier
    
    def __repr__(self) -> str:
        """Representation of the timezone."""
        return f"TimeZone('{self._identifier}')"
    
    def __eq__(self, other) -> bool:
        """Check equality with another timezone."""
        if not isinstance(other, TimeZone):
            return False
        return self._identifier == other._identifier
    
    def __hash__(self) -> int:
        """Hash function for timezone."""
        return hash(self._identifier)
    
    @classmethod
    def from_string(cls, timezone_string: str) -> 'TimeZone':
        """Create a TimeZone from a string identifier."""
        return cls(timezone_string)
    
    @property
    def zone_info(self) -> ZoneInfo:
        """Get the underlying ZoneInfo object."""
        return self._zone_info
