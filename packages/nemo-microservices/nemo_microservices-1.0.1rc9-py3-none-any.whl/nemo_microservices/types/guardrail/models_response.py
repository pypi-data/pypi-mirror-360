# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ..._models import BaseModel
from .models_response_entry import ModelsResponseEntry

__all__ = ["ModelsResponse"]


class ModelsResponse(BaseModel):
    data: Optional[List[ModelsResponseEntry]] = None
    """List of models"""

    object: Optional[str] = None
    """The `data` type"""
