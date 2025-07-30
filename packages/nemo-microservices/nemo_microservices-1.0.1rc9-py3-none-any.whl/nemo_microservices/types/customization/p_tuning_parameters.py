# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from ..._models import BaseModel

__all__ = ["PTuningParameters"]


class PTuningParameters(BaseModel):
    virtual_tokens: int
    """Number of virtual tokens to use for customization.

    Virtual tokens are embeddings inserted into the model prompt that have no
    concrete mapping to strings or characters within the model's vocabulary.
    """
