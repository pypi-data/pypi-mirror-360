# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["UserMessagesConfig"]


class UserMessagesConfig(TypedDict, total=False):
    embeddings_only: bool
    """Whether to use only embeddings for computing the user canonical form messages."""

    embeddings_only_fallback_intent: str
    """Defines the fallback intent when the similarity is below the threshold.

    If set to None, the user intent is computed normally using the LLM. If set to a
    string value, that string is used as the intent.
    """

    embeddings_only_similarity_threshold: float
    """
    The similarity threshold to use when using only embeddings for computing the
    user canonical form messages.
    """
