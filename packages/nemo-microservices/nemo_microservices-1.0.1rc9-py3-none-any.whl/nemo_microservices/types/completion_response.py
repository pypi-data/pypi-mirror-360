# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .._models import BaseModel
from .shared.usage_info import UsageInfo
from .shared.completion_response_choice import CompletionResponseChoice

__all__ = ["CompletionResponse"]


class CompletionResponse(BaseModel):
    choices: List[CompletionResponseChoice]

    model: str

    usage: UsageInfo

    id: Optional[str] = None

    created: Optional[int] = None

    object: Optional[str] = None
