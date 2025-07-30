# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Required, TypedDict

__all__ = ["PTuningFinetuningData"]


class PTuningFinetuningData(TypedDict, total=False):
    token_embeddings: Required[Iterable[Iterable[float]]]
    """
    Learned continuous prompt embeddings that help optimize the model for specific
    tasks.
    """
