# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["Embedding"]


class Embedding(BaseModel):
    embedding: List[float]
    """The embedding vector."""

    index: int
    """The index of the embedding."""

    object: Optional[Literal["embedding"]] = None
