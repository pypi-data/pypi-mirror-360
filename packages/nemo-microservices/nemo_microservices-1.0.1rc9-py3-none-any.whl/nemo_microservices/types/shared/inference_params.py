# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ..._models import BaseModel

__all__ = ["InferenceParams"]


class InferenceParams(BaseModel):
    max_tokens: Optional[int] = None

    stop: Optional[List[str]] = None

    temperature: Optional[float] = None

    top_k: Optional[int] = None

    top_p: Optional[float] = None
