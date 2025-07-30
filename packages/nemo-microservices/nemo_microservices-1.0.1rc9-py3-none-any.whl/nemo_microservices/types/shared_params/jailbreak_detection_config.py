# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["JailbreakDetectionConfig"]


class JailbreakDetectionConfig(TypedDict, total=False):
    embedding: str
    """Model to use for embedding-based detections."""

    length_per_perplexity_threshold: float
    """The length/perplexity threshold."""

    prefix_suffix_perplexity_threshold: float
    """The prefix/suffix perplexity threshold."""

    server_endpoint: str
    """The endpoint for the jailbreak detection heuristics server."""
