# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

from .single_call_config import SingleCallConfig
from .user_messages_config import UserMessagesConfig

__all__ = ["DialogRails"]


class DialogRails(TypedDict, total=False):
    single_call: SingleCallConfig
    """Configuration for the single LLM call option for topical rails."""

    user_messages: UserMessagesConfig
    """Configuration for how the user messages are interpreted."""
