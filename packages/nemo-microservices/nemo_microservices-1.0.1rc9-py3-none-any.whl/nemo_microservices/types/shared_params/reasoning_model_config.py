# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["ReasoningModelConfig"]


class ReasoningModelConfig(TypedDict, total=False):
    end_token: str
    """The end token used for reasoning traces."""

    remove_reasoning_traces: bool
    """For reasoning models (e.g.

    DeepSeek-r1), if the output parser should remove reasoning traces.
    """

    remove_thinking_traces: bool

    start_token: str
    """The start token used for reasoning traces."""
