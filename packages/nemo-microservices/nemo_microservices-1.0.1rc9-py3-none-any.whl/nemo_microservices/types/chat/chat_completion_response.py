# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ..._models import BaseModel
from ..shared.usage_info import UsageInfo
from ..shared.chat_completion_response_choice import ChatCompletionResponseChoice

__all__ = ["ChatCompletionResponse"]


class ChatCompletionResponse(BaseModel):
    choices: List[ChatCompletionResponseChoice]

    model: str

    usage: UsageInfo

    id: Optional[str] = None

    created: Optional[int] = None

    object: Optional[str] = None

    system_fingerprint: Optional[str] = None
    """Represents the backend configuration that the model runs with.

    Used with seed for determinism.
    """
