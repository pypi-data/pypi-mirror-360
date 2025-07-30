# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["MessageTemplate"]


class MessageTemplate(TypedDict, total=False):
    content: Required[str]
    """The content of the message."""

    type: Required[str]
    """The type of message, e.g., 'assistant', 'user', 'system'."""
