# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .._models import BaseModel

__all__ = ["CreatedAtFilter"]


class CreatedAtFilter(BaseModel):
    gte: Optional[str] = None
    """Filter entities created after a given date."""

    lte: Optional[str] = None
    """Filter entities created before a given date."""
