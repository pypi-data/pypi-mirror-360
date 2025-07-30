# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["AutoAlignOptions"]


class AutoAlignOptions(TypedDict, total=False):
    guardrails_config: object
    """The guardrails configuration that is passed to the AutoAlign endpoint"""
