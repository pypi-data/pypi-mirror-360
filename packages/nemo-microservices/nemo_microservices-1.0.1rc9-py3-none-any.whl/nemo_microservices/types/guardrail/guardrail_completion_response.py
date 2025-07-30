# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ..._models import BaseModel
from ..shared.usage_info import UsageInfo
from ..guardrails_data_output import GuardrailsDataOutput
from ..shared.completion_response_choice import CompletionResponseChoice

__all__ = ["GuardrailCompletionResponse"]


class GuardrailCompletionResponse(BaseModel):
    choices: List[CompletionResponseChoice]

    model: str

    usage: UsageInfo

    id: Optional[str] = None

    created: Optional[int] = None

    guardrails_data: Optional[GuardrailsDataOutput] = None
    """The guardrails specific output data."""

    object: Optional[str] = None
