# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime

from ..._models import BaseModel

__all__ = ["StatusLog"]


class StatusLog(BaseModel):
    updated_at: datetime
    """The time when the status was updated."""

    detail: Optional[str] = None
    """Optional details for the status of the job."""

    message: Optional[str] = None
    """Optional message for the status of the job."""
