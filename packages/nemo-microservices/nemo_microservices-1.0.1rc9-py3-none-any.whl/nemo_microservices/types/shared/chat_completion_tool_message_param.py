# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["ChatCompletionToolMessageParam"]


class ChatCompletionToolMessageParam(BaseModel):
    content: str
    """The contents of the tool message."""

    role: Literal["tool"]
    """The role of the messages author, in this case `tool`."""

    tool_call_id: str
    """Tool call that this message is responding to."""
