# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel

__all__ = ["JailbreakDetectionConfig"]


class JailbreakDetectionConfig(BaseModel):
    embedding: Optional[str] = None
    """Model to use for embedding-based detections."""

    length_per_perplexity_threshold: Optional[float] = None
    """The length/perplexity threshold."""

    prefix_suffix_perplexity_threshold: Optional[float] = None
    """The prefix/suffix perplexity threshold."""

    server_endpoint: Optional[str] = None
    """The endpoint for the jailbreak detection heuristics server."""
