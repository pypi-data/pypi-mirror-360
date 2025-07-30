# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel
from .private_ai_detection_options import PrivateAIDetectionOptions

__all__ = ["PrivateAIDetection"]


class PrivateAIDetection(BaseModel):
    input: Optional[PrivateAIDetectionOptions] = None
    """Configuration options for Private AI."""

    output: Optional[PrivateAIDetectionOptions] = None
    """Configuration options for Private AI."""

    retrieval: Optional[PrivateAIDetectionOptions] = None
    """Configuration options for Private AI."""

    server_endpoint: Optional[str] = None
    """The endpoint for the private AI detection server."""
