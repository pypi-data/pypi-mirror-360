# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import TypedDict

__all__ = ["PrivateAIDetectionOptions"]


class PrivateAIDetectionOptions(TypedDict, total=False):
    entities: List[str]
    """The list of entities that should be detected."""
