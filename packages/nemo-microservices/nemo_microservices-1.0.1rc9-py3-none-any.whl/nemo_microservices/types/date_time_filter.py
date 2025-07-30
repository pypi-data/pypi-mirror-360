# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .._models import BaseModel

__all__ = ["DateTimeFilter"]


class DateTimeFilter(BaseModel):
    eq: Optional[str] = None
    """Filter for dates equal to this value."""

    gt: Optional[str] = None
    """Filter for dates greater than this value."""

    gte: Optional[str] = None
    """Filter for dates greater than or equal to this value."""

    lt: Optional[str] = None
    """Filter for dates less than this value."""

    lte: Optional[str] = None
    """Filter for dates less than or equal to this value."""

    neq: Optional[str] = None
    """Filter for dates not equal to this value."""
