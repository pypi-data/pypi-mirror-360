# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel

__all__ = ["JobWarning"]


class JobWarning(BaseModel):
    explanation: Optional[str] = None
    """Explanation of the warning"""

    message: Optional[str] = None
    """Warning message"""
