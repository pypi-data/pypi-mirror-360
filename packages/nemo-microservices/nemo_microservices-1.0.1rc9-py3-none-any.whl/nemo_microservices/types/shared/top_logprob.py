# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ..._models import BaseModel

__all__ = ["TopLogprob"]


class TopLogprob(BaseModel):
    token: str
    """The token."""

    logprob: float
    """The log probability of this token."""

    bytes: Optional[List[int]] = None
    """UTF-8 bytes representation of the token."""
