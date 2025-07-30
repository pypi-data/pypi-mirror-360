# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .._models import BaseModel
from .llm_call_info import LlmCallInfo

__all__ = ["ExecutedAction"]


class ExecutedAction(BaseModel):
    action_name: str
    """The name of the action that was executed."""

    action_params: Optional[object] = None
    """The parameters for the action."""

    duration: Optional[float] = None
    """How long the action took to execute, in seconds."""

    finished_at: Optional[float] = None
    """Timestamp for when the action finished."""

    llm_calls: Optional[List[LlmCallInfo]] = None
    """Information about the LLM calls made by the action."""

    return_value: Optional[object] = None
    """The value returned by the action."""

    started_at: Optional[float] = None
    """Timestamp for when the action started."""
