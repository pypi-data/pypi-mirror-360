# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["ProjectFilterParam"]


class ProjectFilterParam(TypedDict, total=False):
    name: str
    """Filter by project name."""

    namespace: str
    """Filter by namespace id."""
