# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["DatasetFilterParam"]


class DatasetFilterParam(TypedDict, total=False):
    namespace: str
    """Filter by namespace id."""

    project: str
    """Filter by project name."""
