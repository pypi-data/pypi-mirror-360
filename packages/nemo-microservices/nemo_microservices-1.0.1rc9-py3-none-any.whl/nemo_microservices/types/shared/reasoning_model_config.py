# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel

__all__ = ["ReasoningModelConfig"]


class ReasoningModelConfig(BaseModel):
    end_token: Optional[str] = None
    """The end token used for reasoning traces."""

    remove_reasoning_traces: Optional[bool] = None
    """For reasoning models (e.g.

    DeepSeek-r1), if the output parser should remove reasoning traces.
    """

    remove_thinking_traces: Optional[bool] = None

    start_token: Optional[str] = None
    """The start token used for reasoning traces."""
