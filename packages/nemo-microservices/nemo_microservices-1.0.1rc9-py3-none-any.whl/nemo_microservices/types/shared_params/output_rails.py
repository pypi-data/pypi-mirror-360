# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import TypedDict

from .output_rails_streaming_config import OutputRailsStreamingConfig

__all__ = ["OutputRails"]


class OutputRails(TypedDict, total=False):
    apply_to_reasoning_traces: bool
    """
    If True, output rails will apply guardrails to both reasoning traces and output
    response. If False, output rails will only apply guardrails to the output
    response excluding the reasoning traces, thus keeping reasoning traces
    unaltered.
    """

    flows: List[str]
    """The names of all the flows that implement output rails."""

    streaming: OutputRailsStreamingConfig
    """Configuration for managing streaming output of LLM tokens."""
