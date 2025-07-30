# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["FactCheckingRailConfig"]


class FactCheckingRailConfig(TypedDict, total=False):
    fallback_to_self_check: bool
    """Whether to fall back to self-check if another method fail."""

    parameters: object
