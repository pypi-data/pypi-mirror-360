# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .._models import BaseModel

__all__ = ["GenerationStats"]


class GenerationStats(BaseModel):
    dialog_rails_duration: Optional[float] = None
    """The time in seconds spent in processing the dialog rails."""

    generation_rails_duration: Optional[float] = None
    """The time in seconds spent in generation rails."""

    input_rails_duration: Optional[float] = None
    """The time in seconds spent in processing the input rails."""

    llm_calls_count: Optional[int] = None
    """The number of LLM calls in total."""

    llm_calls_duration: Optional[float] = None
    """The time in seconds spent in LLM calls."""

    llm_calls_total_completion_tokens: Optional[int] = None
    """The total number of completion tokens."""

    llm_calls_total_prompt_tokens: Optional[int] = None
    """The total number of prompt tokens."""

    llm_calls_total_tokens: Optional[int] = None
    """The total number of tokens."""

    output_rails_duration: Optional[float] = None
    """The time in seconds spent in processing the output rails."""

    total_duration: Optional[float] = None
    """The total time in seconds."""
