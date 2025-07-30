# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel
from .single_call_config import SingleCallConfig
from .user_messages_config import UserMessagesConfig

__all__ = ["DialogRails"]


class DialogRails(BaseModel):
    single_call: Optional[SingleCallConfig] = None
    """Configuration for the single LLM call option for topical rails."""

    user_messages: Optional[UserMessagesConfig] = None
    """Configuration for how the user messages are interpreted."""
