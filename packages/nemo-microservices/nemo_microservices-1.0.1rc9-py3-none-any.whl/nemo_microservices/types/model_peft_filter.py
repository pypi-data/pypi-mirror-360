# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .._models import BaseModel

__all__ = ["ModelPeftFilter"]


class ModelPeftFilter(BaseModel):
    lora: Optional[bool] = None
    """Filter models with LoRA fine-tuning."""
