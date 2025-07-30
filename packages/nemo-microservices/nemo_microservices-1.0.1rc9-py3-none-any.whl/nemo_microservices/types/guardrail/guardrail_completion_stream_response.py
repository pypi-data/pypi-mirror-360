# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ..._models import BaseModel
from ..shared.usage_info import UsageInfo
from ..shared.completion_response_stream_choice import CompletionResponseStreamChoice

__all__ = ["GuardrailCompletionStreamResponse"]


class GuardrailCompletionStreamResponse(BaseModel):
    choices: List[CompletionResponseStreamChoice]

    model: str

    id: Optional[str] = None

    created: Optional[int] = None

    object: Optional[str] = None

    usage: Optional[UsageInfo] = None
