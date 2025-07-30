# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel

__all__ = ["ModelsResponseEntry"]


class ModelsResponseEntry(BaseModel):
    id: Optional[str] = None
    """Unique identifier for Model"""

    created: Optional[int] = None
    """Epoch time in seconds when model was created"""

    object: Optional[str] = None
    """Unique identifier for Model"""

    owned_by: Optional[str] = None
    """Model Owner"""
