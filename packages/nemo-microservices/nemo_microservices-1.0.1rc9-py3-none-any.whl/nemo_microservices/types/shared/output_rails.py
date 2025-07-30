# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ..._models import BaseModel
from .output_rails_streaming_config import OutputRailsStreamingConfig

__all__ = ["OutputRails"]


class OutputRails(BaseModel):
    apply_to_reasoning_traces: Optional[bool] = None
    """
    If True, output rails will apply guardrails to both reasoning traces and output
    response. If False, output rails will only apply guardrails to the output
    response excluding the reasoning traces, thus keeping reasoning traces
    unaltered.
    """

    flows: Optional[List[str]] = None
    """The names of all the flows that implement output rails."""

    streaming: Optional[OutputRailsStreamingConfig] = None
    """Configuration for managing streaming output of LLM tokens."""
