# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["SftParametersParam"]


class SftParametersParam(TypedDict, total=False):
    attention_dropout: float
    """Dropout probability for attention."""

    hidden_dropout: float
    """Dropout probability for hidden state transformer."""
