# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["ModelSpecDeParam"]


class ModelSpecDeParam(TypedDict, total=False):
    context_size: Required[int]

    is_chat: Required[bool]
    """Whether or not this is a chat model"""

    num_parameters: Required[int]

    num_virtual_tokens: Required[int]
