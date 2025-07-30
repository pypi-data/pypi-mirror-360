# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ..._models import BaseModel

__all__ = ["PrivateAIDetectionOptions"]


class PrivateAIDetectionOptions(BaseModel):
    entities: Optional[List[str]] = None
    """The list of entities that should be detected."""
