# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ...._models import BaseModel
from ...shared.chat_completion_response_stream_choice import ChatCompletionResponseStreamChoice

__all__ = ["GuardrailChatCompletionStreamResponse"]


class GuardrailChatCompletionStreamResponse(BaseModel):
    choices: List[ChatCompletionResponseStreamChoice]

    model: str

    id: Optional[str] = None

    created: Optional[int] = None

    object: Optional[str] = None

    system_fingerprint: Optional[str] = None
    """Represents the backend configuration that the model runs with.

    Used with seed for determinism.
    """
