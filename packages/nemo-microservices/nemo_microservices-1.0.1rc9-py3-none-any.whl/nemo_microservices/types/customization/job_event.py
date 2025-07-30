# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel

__all__ = ["JobEvent"]


class JobEvent(BaseModel):
    count: Optional[str] = None
    """Times this event was seen"""

    first_seen: Optional[int] = None
    """First time it was seen, timestamp"""

    last_seen: Optional[int] = None
    """Last time it was seen, timestamp"""

    message: Optional[str] = None
    """Event Message"""

    reason: Optional[str] = None
    """Event Reason"""

    type: Optional[str] = None
    """Event Type"""
