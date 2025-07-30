# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Union, Optional
from typing_extensions import Literal, TypeAlias

from ..._models import BaseModel
from .chat_completion_content_part_text_param import ChatCompletionContentPartTextParam
from .chat_completion_content_part_image_param import ChatCompletionContentPartImageParam

__all__ = ["ChatCompletionUserMessageParam", "ContentUnionMember1"]

ContentUnionMember1: TypeAlias = Union[ChatCompletionContentPartTextParam, ChatCompletionContentPartImageParam]


class ChatCompletionUserMessageParam(BaseModel):
    content: Union[str, List[ContentUnionMember1]]
    """The contents of the user message."""

    role: Literal["user"]
    """The role of the messages author, in this case `user`."""

    name: Optional[str] = None
    """An optional name for the participant."""
