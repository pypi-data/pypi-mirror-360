# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["ReasoningParams"]


class ReasoningParams(TypedDict, total=False):
    effort: str
    """
    Option for OpenAI models to specify low, medium, or high reasoning effort which
    balances between speed and reasoning accuracy.
    """

    end_token: str
    """
    Configure the end token to trim reasoning context based on the model's reasoning
    API. Used for omitting Nemotron reasoning steps from output denoted with
    </think> tags
    """
