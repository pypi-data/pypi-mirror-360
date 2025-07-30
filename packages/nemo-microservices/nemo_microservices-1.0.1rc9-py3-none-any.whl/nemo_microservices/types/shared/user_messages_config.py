# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel

__all__ = ["UserMessagesConfig"]


class UserMessagesConfig(BaseModel):
    embeddings_only: Optional[bool] = None
    """Whether to use only embeddings for computing the user canonical form messages."""

    embeddings_only_fallback_intent: Optional[str] = None
    """Defines the fallback intent when the similarity is below the threshold.

    If set to None, the user intent is computed normally using the LLM. If set to a
    string value, that string is used as the intent.
    """

    embeddings_only_similarity_threshold: Optional[float] = None
    """
    The similarity threshold to use when using only embeddings for computing the
    user canonical form messages.
    """
