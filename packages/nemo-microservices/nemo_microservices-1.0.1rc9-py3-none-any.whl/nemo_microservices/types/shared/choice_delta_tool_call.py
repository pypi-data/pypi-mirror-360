# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel
from .choice_delta_tool_call_function import ChoiceDeltaToolCallFunction

__all__ = ["ChoiceDeltaToolCall"]


class ChoiceDeltaToolCall(BaseModel):
    index: int

    id: Optional[str] = None

    function: Optional[ChoiceDeltaToolCallFunction] = None

    type: Optional[str] = None
