# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["PTuningParametersParam"]


class PTuningParametersParam(TypedDict, total=False):
    virtual_tokens: Required[int]
    """Number of virtual tokens to use for customization.

    Virtual tokens are embeddings inserted into the model prompt that have no
    concrete mapping to strings or characters within the model's vocabulary.
    """
