# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List

from ..._models import BaseModel

__all__ = ["PTuningFinetuningData"]


class PTuningFinetuningData(BaseModel):
    token_embeddings: List[List[float]]
    """
    Learned continuous prompt embeddings that help optimize the model for specific
    tasks.
    """
