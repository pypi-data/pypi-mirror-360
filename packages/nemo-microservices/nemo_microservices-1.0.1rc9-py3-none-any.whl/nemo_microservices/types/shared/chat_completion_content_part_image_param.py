# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ..._models import BaseModel
from .image_url import ImageURL

__all__ = ["ChatCompletionContentPartImageParam"]


class ChatCompletionContentPartImageParam(BaseModel):
    image_url: ImageURL
    """The image URL information."""

    type: Literal["image_url"]
    """The type of the content part."""
