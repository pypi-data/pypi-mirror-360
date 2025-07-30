# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime

from ..._models import BaseModel

__all__ = ["VersionTag"]


class VersionTag(BaseModel):
    name: str
    """The name of the version.

    Typically should be kept lower case, no space, no '/', no `@`.
    """

    created_at: Optional[datetime] = None
    """Timestamp for when the version tag was created."""

    created_by: Optional[str] = None
    """The ID of the user that created this entity."""
