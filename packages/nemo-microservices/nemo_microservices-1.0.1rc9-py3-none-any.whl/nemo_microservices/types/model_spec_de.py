# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from .._models import BaseModel

__all__ = ["ModelSpecDe"]


class ModelSpecDe(BaseModel):
    context_size: int

    is_chat: bool
    """Whether or not this is a chat model"""

    num_parameters: int

    num_virtual_tokens: int
