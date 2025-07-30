# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel

__all__ = ["ImageURL"]


class ImageURL(BaseModel):
    url: str
    """Either a URL of the image or the base64 encoded image data."""

    detail: Optional[str] = None
    """Specifies the detail level of the image."""
