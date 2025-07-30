# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

from .function import Function

__all__ = ["ChatCompletionMessageToolCallParam"]


class ChatCompletionMessageToolCallParam(TypedDict, total=False):
    id: Required[str]
    """The ID of the tool call."""

    function: Required[Function]
    """The function that the model called."""

    type: Required[Literal["function"]]
    """The type of the tool. Currently, only `function` is supported."""
