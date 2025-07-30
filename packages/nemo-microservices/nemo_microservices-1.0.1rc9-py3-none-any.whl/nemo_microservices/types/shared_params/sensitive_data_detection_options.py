# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import TypedDict

__all__ = ["SensitiveDataDetectionOptions"]


class SensitiveDataDetectionOptions(TypedDict, total=False):
    entities: List[str]
    """The list of entities that should be detected.

    Check out https://microsoft.github.io/presidio/supported_entities/ forthe list
    of supported entities.
    """

    mask_token: str
    """The token that should be used to mask the sensitive data."""

    score_threshold: float
    """The score threshold that should be used to detect the sensitive data."""
