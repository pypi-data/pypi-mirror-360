# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ..._models import BaseModel
from .top_logprob import TopLogprob

__all__ = ["ChatCompletionTokenLogprob"]


class ChatCompletionTokenLogprob(BaseModel):
    token: str
    """The token."""

    logprob: float
    """The log probability of this token."""

    bytes: Optional[List[int]] = None
    """UTF-8 bytes representation of the token."""

    top_logprobs: Optional[List[TopLogprob]] = None
    """List of the most likely tokens and their log probability at this position."""
