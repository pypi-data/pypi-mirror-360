# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel

__all__ = ["SftParameters"]


class SftParameters(BaseModel):
    attention_dropout: Optional[float] = None
    """Dropout probability for attention."""

    hidden_dropout: Optional[float] = None
    """Dropout probability for hidden state transformer."""
