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

# Import datetime timezone for basic UTC support as fallback
from datetime import timezone as dt_timezone


class TimeZone:
    """Represents a time zone."""

    def __init__(self, identifier: str):
        """Initialize a TimeZone with the given identifier."""
        try:
            self._zone_info = ZoneInfo(identifier)
            self._identifier = identifier
        except Exception as e:
            # Fallback for Windows when tzdata is not available
            if identifier.upper() == "UTC":
                self._zone_info = dt_timezone.utc
                self._identifier = identifier
            else:
                # Try to handle common timezone abbreviations as UTC offsets
                if self._try_parse_offset(identifier):
                    return
                raise InvalidArgumentError(
                    f"Invalid timezone identifier: {identifier}. On Windows, install tzdata package for full timezone support."
                ) from e

    def _try_parse_offset(self, identifier: str) -> bool:
        """Try to parse timezone as UTC offset (e.g., '+05:00', '-08:00')."""
        import re

        # Match patterns like +05:00, -08:00, +0530, etc.
        offset_pattern = r"^([+-])(\d{1,2}):?(\d{2})$"
        match = re.match(offset_pattern, identifier)

        if match:
            sign, hours_str, minutes_str = match.groups()
            hours = int(hours_str)
            minutes = int(minutes_str)

            if hours > 23 or minutes > 59:
                return False

            total_minutes = hours * 60 + minutes
            if sign == "-":
                total_minutes = -total_minutes

            from datetime import timedelta

            self._zone_info = dt_timezone(timedelta(minutes=total_minutes))
            self._identifier = identifier
            return True

        return False

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

    def __eq__(self, other: object) -> bool:
        """Check equality with another timezone."""
        if not isinstance(other, TimeZone):
            return False
        return self._identifier == other._identifier

    def __hash__(self) -> int:
        """Hash function for timezone."""
        return hash(self._identifier)

    @classmethod
    def from_string(cls, timezone_string: str) -> "TimeZone":
        """Create a TimeZone from a string identifier."""
        return cls(timezone_string)

    @property
    def zone_info(self):
        """Get the underlying timezone object (ZoneInfo or datetime.timezone)."""
        return self._zone_info
