# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel

__all__ = ["FactCheckingRailConfig"]


class FactCheckingRailConfig(BaseModel):
    fallback_to_self_check: Optional[bool] = None
    """Whether to fall back to self-check if another method fail."""

    parameters: Optional[object] = None
