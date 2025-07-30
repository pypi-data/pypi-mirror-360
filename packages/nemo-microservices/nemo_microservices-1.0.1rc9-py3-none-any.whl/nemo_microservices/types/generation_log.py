# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .._models import BaseModel
from .llm_call_info import LlmCallInfo
from .activated_rail import ActivatedRail
from .generation_stats import GenerationStats

__all__ = ["GenerationLog"]


class GenerationLog(BaseModel):
    activated_rails: Optional[List[ActivatedRail]] = None
    """The list of rails that were activated during generation."""

    colang_history: Optional[str] = None
    """The Colang history associated with the generation."""

    internal_events: Optional[List[object]] = None
    """The complete sequence of internal events generated."""

    llm_calls: Optional[List[LlmCallInfo]] = None
    """The list of LLM calls that have been made to fulfill the generation request."""

    stats: Optional[GenerationStats] = None
    """General stats about the generation."""
