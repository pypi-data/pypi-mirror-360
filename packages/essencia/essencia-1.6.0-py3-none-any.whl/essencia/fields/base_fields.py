"""
Base field types for Pydantic models.

Provides common field types used throughout the application.
"""

import datetime
from typing import Annotated, Optional, Any
from pydantic import Field, BeforeValidator

# Helper functions for date/time handling
def today() -> datetime.date:
    """Get today's date."""
    return datetime.date.today()


def now() -> datetime.datetime:
    """Get current datetime."""
    return datetime.datetime.now()


def string_to_date(value: Any) -> Optional[datetime.date]:
    """Convert string to date."""
    if value is None:
        return None
    if isinstance(value, datetime.date):
        return value
    if isinstance(value, datetime.datetime):
        return value.date()
    if isinstance(value, str):
        try:
            # Try parsing ISO format
            return datetime.datetime.fromisoformat(value).date()
        except ValueError:
            # Try parsing common formats
            for fmt in ["%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"]:
                try:
                    return datetime.datetime.strptime(value, fmt).date()
                except ValueError:
                    continue
    return None


def parse_date_to_datetime(value: Any) -> Optional[datetime.datetime]:
    """Convert date to datetime."""
    if value is None:
        return None
    if isinstance(value, datetime.datetime):
        return value
    if isinstance(value, datetime.date):
        return datetime.datetime.combine(value, datetime.time.min)
    if isinstance(value, str):
        try:
            return datetime.datetime.fromisoformat(value)
        except ValueError:
            # Try parsing common formats
            for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%d/%m/%Y %H:%M:%S", "%d/%m/%Y"]:
                try:
                    return datetime.datetime.strptime(value, fmt)
                except ValueError:
                    continue
    return None


def slice_if_not_none(value: Any, length: Optional[int] = None) -> Any:
    """Slice string if not None."""
    if value is None:
        return None
    if isinstance(value, str) and length is not None:
        return value[:length]
    return value


# Field type definitions
DefaultDate = Annotated[
    datetime.date, 
    Field(default_factory=today), 
    BeforeValidator(lambda x: string_to_date(slice_if_not_none(x)))
]

DefaultDateTime = Annotated[
    datetime.datetime, 
    Field(default_factory=now), 
    BeforeValidator(lambda x: parse_date_to_datetime(string_to_date(slice_if_not_none(x, 19))))
]

OptionalDate = Annotated[Optional[datetime.date], Field(None)]
OptionalDateTime = Annotated[Optional[datetime.datetime], Field(None)]

# Optional strings
OptionalString = Annotated[Optional[str], Field(default=None)]

# Export field types
__all__ = [
    'DefaultDate',
    'DefaultDateTime',
    'OptionalDate', 
    'OptionalDateTime',
    'OptionalString',
    # Helper functions
    'today',
    'now',
    'string_to_date',
    'parse_date_to_datetime',
    'slice_if_not_none'
]