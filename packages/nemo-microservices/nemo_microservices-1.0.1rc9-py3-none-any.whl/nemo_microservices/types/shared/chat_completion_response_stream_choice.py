# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel
from .delta_message import DeltaMessage
from .choice_logprobs import ChoiceLogprobs

__all__ = ["ChatCompletionResponseStreamChoice"]


class ChatCompletionResponseStreamChoice(BaseModel):
    delta: DeltaMessage

    index: int

    finish_reason: Optional[str] = None

    logprobs: Optional[ChoiceLogprobs] = None
    """Log probability information for a chat completion choice.

    This is used in both regular and streaming chat completions when logprobs=true
    is provided in the request.
    """
