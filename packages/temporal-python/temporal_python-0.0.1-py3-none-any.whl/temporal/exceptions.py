"""
Exception classes for the Temporal API.
"""

class TemporalError(Exception):
    """Base exception for all Temporal API errors."""
    pass


class RangeError(TemporalError):
    """Raised when a value is outside the valid range."""
    pass


class TemporalTypeError(TemporalError):
    """Raised when an operation receives an inappropriate type."""
    pass


class InvalidArgumentError(TemporalError):
    """Raised when an invalid argument is provided."""
    pass
