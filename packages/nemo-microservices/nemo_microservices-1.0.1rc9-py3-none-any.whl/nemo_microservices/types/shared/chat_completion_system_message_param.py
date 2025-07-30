# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["ChatCompletionSystemMessageParam"]


class ChatCompletionSystemMessageParam(BaseModel):
    content: str
    """The contents of the system message."""

    role: Literal["system"]
    """The role of the messages author, in this case `system`."""

    name: Optional[str] = None
    """An optional name for the participant."""
