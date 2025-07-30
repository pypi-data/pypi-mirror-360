# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["GenerationLogOptionsParam"]


class GenerationLogOptionsParam(TypedDict, total=False):
    activated_rails: bool
    """
    Include detailed information about the rails that were activated during
    generation.
    """

    colang_history: bool
    """Include the history of the conversation in Colang format."""

    internal_events: bool
    """Include the array of internal generated events."""

    llm_calls: bool
    """Include information about all the LLM calls that were made.

    This includes: prompt, completion, token usage, raw response, etc.
    """
