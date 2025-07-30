# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from ..._models import BaseModel

__all__ = ["MessageTemplate"]


class MessageTemplate(BaseModel):
    content: str
    """The content of the message."""

    type: str
    """The type of message, e.g., 'assistant', 'user', 'system'."""
