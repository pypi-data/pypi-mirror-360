# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel

__all__ = ["OutputRailsStreamingConfig"]


class OutputRailsStreamingConfig(BaseModel):
    chunk_size: Optional[int] = None
    """The number of tokens in each processing chunk.

    This is the size of the token block on which output rails are applied.
    """

    context_size: Optional[int] = None
    """
    The number of tokens carried over from the previous chunk to provide context for
    continuity in processing.
    """

    enabled: Optional[bool] = None
    """Enables streaming mode when True."""

    stream_first: Optional[bool] = None
    """If True, token chunks are streamed immediately before output rails are applied."""
