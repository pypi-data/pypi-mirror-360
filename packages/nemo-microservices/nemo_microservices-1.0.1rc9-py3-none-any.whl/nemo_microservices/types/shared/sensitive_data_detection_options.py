# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ..._models import BaseModel

__all__ = ["SensitiveDataDetectionOptions"]


class SensitiveDataDetectionOptions(BaseModel):
    entities: Optional[List[str]] = None
    """The list of entities that should be detected.

    Check out https://microsoft.github.io/presidio/supported_entities/ forthe list
    of supported entities.
    """

    mask_token: Optional[str] = None
    """The token that should be used to mask the sensitive data."""

    score_threshold: Optional[float] = None
    """The score threshold that should be used to detect the sensitive data."""
