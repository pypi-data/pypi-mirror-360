# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Union, Optional
from typing_extensions import TypeAlias

from ..._models import BaseModel
from .choice_delta_tool_call import ChoiceDeltaToolCall
from .choice_delta_function_call import ChoiceDeltaFunctionCall
from .chat_completion_content_part_text_param import ChatCompletionContentPartTextParam
from .chat_completion_content_part_image_param import ChatCompletionContentPartImageParam

__all__ = ["DeltaMessage", "ContentUnionMember1"]

ContentUnionMember1: TypeAlias = Union[ChatCompletionContentPartTextParam, ChatCompletionContentPartImageParam]


class DeltaMessage(BaseModel):
    content: Union[str, List[ContentUnionMember1], None] = None

    function_call: Optional[ChoiceDeltaFunctionCall] = None

    role: Optional[str] = None

    tool_calls: Optional[List[ChoiceDeltaToolCall]] = None
