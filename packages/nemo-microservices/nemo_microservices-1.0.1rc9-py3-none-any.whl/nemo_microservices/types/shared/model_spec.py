# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from ..._models import BaseModel

__all__ = ["ModelSpec"]


class ModelSpec(BaseModel):
    context_size: int
    """
    The maximum number of tokens to process together in a single forward pass
    through the model.
    """

    is_chat: bool
    """
    Indicates if the model is designed for multi-turn conversation rather than
    single-prompt completion.
    """

    num_parameters: int
    """
    The total number of trainable parameters in the model's neural network
    architecture.
    """

    num_virtual_tokens: int
    """
    The number of virtual tokens the model can support for techniques such as prompt
    tuning, where special trainable embeddings are prepended to inputs.
    """
