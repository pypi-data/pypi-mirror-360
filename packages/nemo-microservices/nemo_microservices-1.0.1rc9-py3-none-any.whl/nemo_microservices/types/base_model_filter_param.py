# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["BaseModelFilterParam"]


class BaseModelFilterParam(TypedDict, total=False):
    name: str
    """Filter by name of the base model."""
