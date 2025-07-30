# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel
from .log_probs import LogProbs

__all__ = ["CompletionResponseStreamChoice"]


class CompletionResponseStreamChoice(BaseModel):
    index: int

    text: str

    finish_reason: Optional[str] = None
    """The reasons why the conversation ended."""

    logprobs: Optional[LogProbs] = None
    """Log probability information for regular (non-chat) completions."""
