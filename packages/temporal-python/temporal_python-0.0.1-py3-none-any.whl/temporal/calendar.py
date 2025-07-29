"""
Calendar system implementation for the Temporal API.
"""

from typing import Dict, Any
from .exceptions import InvalidArgumentError


class Calendar:
    """Represents a calendar system."""
    
    def __init__(self, identifier: str = "iso8601"):
        """Initialize a Calendar with the given identifier."""
        if identifier not in ["iso8601"]:
            raise InvalidArgumentError(f"Unsupported calendar: {identifier}")
        self._identifier = identifier
    
    @property
    def id(self) -> str:
        """Get the calendar identifier."""
        return self._identifier
    
    def __str__(self) -> str:
        """String representation of the calendar."""
        return self._identifier
    
    def __repr__(self) -> str:
        """Representation of the calendar."""
        return f"Calendar('{self._identifier}')"
    
    def __eq__(self, other) -> bool:
        """Check equality with another calendar."""
        if not isinstance(other, Calendar):
            return False
        return self._identifier == other._identifier
    
    def __hash__(self) -> int:
        """Hash function for calendar."""
        return hash(self._identifier)
    
    @classmethod
    def from_string(cls, calendar_string: str) -> 'Calendar':
        """Create a Calendar from a string identifier."""
        return cls(calendar_string)
