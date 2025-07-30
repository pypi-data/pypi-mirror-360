# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["ModelSpec"]


class ModelSpec(TypedDict, total=False):
    context_size: Required[int]
    """
    The maximum number of tokens to process together in a single forward pass
    through the model.
    """

    is_chat: Required[bool]
    """
    Indicates if the model is designed for multi-turn conversation rather than
    single-prompt completion.
    """

    num_parameters: Required[int]
    """
    The total number of trainable parameters in the model's neural network
    architecture.
    """

    num_virtual_tokens: Required[int]
    """
    The number of virtual tokens the model can support for techniques such as prompt
    tuning, where special trainable embeddings are prepended to inputs.
    """
