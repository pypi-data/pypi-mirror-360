# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .._models import BaseModel

__all__ = ["BaseModelFilter"]


class BaseModelFilter(BaseModel):
    name: Optional[str] = None
    """Filter by name of the base model."""
