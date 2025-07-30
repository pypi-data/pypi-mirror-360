# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["DateTimeFilterParam"]


class DateTimeFilterParam(TypedDict, total=False):
    eq: str
    """Filter for dates equal to this value."""

    gt: str
    """Filter for dates greater than this value."""

    gte: str
    """Filter for dates greater than or equal to this value."""

    lt: str
    """Filter for dates less than this value."""

    lte: str
    """Filter for dates less than or equal to this value."""

    neq: str
    """Filter for dates not equal to this value."""
