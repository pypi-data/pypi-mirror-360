# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import TypedDict

__all__ = ["InferenceParams"]


class InferenceParams(TypedDict, total=False):
    max_tokens: int

    stop: List[str]

    temperature: float

    top_k: int

    top_p: float
