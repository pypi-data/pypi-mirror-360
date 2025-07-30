# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["CreatedAtFilterParam"]


class CreatedAtFilterParam(TypedDict, total=False):
    gte: str
    """Filter entities created after a given date."""

    lte: str
    """Filter entities created before a given date."""
