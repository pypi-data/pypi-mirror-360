# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

from .auto_align_options import AutoAlignOptions

__all__ = ["AutoAlignRailConfig"]


class AutoAlignRailConfig(TypedDict, total=False):
    input: AutoAlignOptions
    """List of guardrails that are activated"""

    output: AutoAlignOptions
    """List of guardrails that are activated"""

    parameters: object
