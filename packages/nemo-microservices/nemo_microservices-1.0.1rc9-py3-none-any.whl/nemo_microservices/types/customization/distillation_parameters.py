# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from ..._models import BaseModel

__all__ = ["DistillationParameters"]


class DistillationParameters(BaseModel):
    teacher: str
    """Target to be used as teacher for distillation."""
