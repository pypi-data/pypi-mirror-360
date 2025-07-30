# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Union
from typing_extensions import Required, TypedDict

__all__ = ["EmbeddingCreateParams"]


class EmbeddingCreateParams(TypedDict, total=False):
    input: Required[Union[str, List[str]]]
    """Input text to embed, encoded as a string or array of tokens."""

    model: Required[str]
    """The model to use. Must be one of the available models."""

    dimensions: int
    """The dimensionality of the embedding vector."""

    encoding_format: str
    """The encoding format of the input."""

    input_type: str
    """The type of the input."""

    truncate: str
    """Truncate the input text."""

    user: str
    """Not Supported. A unique identifier representing your end-user."""
