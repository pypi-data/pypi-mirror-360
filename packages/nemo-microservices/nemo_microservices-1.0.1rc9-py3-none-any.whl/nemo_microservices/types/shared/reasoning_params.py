# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel

__all__ = ["ReasoningParams"]


class ReasoningParams(BaseModel):
    effort: Optional[str] = None
    """
    Option for OpenAI models to specify low, medium, or high reasoning effort which
    balances between speed and reasoning accuracy.
    """

    end_token: Optional[str] = None
    """
    Configure the end token to trim reasoning context based on the model's reasoning
    API. Used for omitting Nemotron reasoning steps from output denoted with
    </think> tags
    """
