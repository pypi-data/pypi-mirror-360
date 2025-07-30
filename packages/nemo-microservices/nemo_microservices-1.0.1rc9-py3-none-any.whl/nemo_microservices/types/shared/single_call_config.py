# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel

__all__ = ["SingleCallConfig"]


class SingleCallConfig(BaseModel):
    enabled: Optional[bool] = None

    fallback_to_multiple_calls: Optional[bool] = None
    """Whether to fall back to multiple calls if a single call is not possible."""
