# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["OutputRailsStreamingConfig"]


class OutputRailsStreamingConfig(TypedDict, total=False):
    chunk_size: int
    """The number of tokens in each processing chunk.

    This is the size of the token block on which output rails are applied.
    """

    context_size: int
    """
    The number of tokens carried over from the previous chunk to provide context for
    continuity in processing.
    """

    enabled: bool
    """Enables streaming mode when True."""

    stream_first: bool
    """If True, token chunks are streamed immediately before output rails are applied."""
