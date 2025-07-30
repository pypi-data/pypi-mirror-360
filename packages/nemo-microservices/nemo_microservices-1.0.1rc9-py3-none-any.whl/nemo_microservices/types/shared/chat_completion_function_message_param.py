# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["ChatCompletionFunctionMessageParam"]


class ChatCompletionFunctionMessageParam(BaseModel):
    content: str
    """The contents of the function message."""

    name: str
    """The name of the function to call."""

    role: Literal["function"]
    """The role of the messages author, in this case `function`."""
