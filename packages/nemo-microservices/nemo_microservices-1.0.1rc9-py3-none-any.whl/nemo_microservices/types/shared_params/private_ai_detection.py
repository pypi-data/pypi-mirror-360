# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

from .private_ai_detection_options import PrivateAIDetectionOptions

__all__ = ["PrivateAIDetection"]


class PrivateAIDetection(TypedDict, total=False):
    input: PrivateAIDetectionOptions
    """Configuration options for Private AI."""

    output: PrivateAIDetectionOptions
    """Configuration options for Private AI."""

    retrieval: PrivateAIDetectionOptions
    """Configuration options for Private AI."""

    server_endpoint: str
    """The endpoint for the private AI detection server."""
