# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["SingleCallConfig"]


class SingleCallConfig(TypedDict, total=False):
    enabled: bool

    fallback_to_multiple_calls: bool
    """Whether to fall back to multiple calls if a single call is not possible."""
