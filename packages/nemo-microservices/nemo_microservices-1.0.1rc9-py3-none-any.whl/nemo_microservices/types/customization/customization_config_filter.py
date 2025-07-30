# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel

__all__ = ["CustomizationConfigFilter"]


class CustomizationConfigFilter(BaseModel):
    enabled: Optional[bool] = None
    """Filter by whether the target is enabled or not for customization"""

    finetuning_type: Optional[str] = None
    """Filter by the finetuning type"""

    name: Optional[str] = None
    """Filter by the name of the customization config"""

    target_base_model: Optional[str] = None
    """Filter by name of the target's base model."""

    target_name: Optional[str] = None
    """Filter by name of the target."""

    training_type: Optional[str] = None
    """Filter by the training type"""
