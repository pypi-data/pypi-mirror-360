# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel

__all__ = ["DeleteResponse"]


class DeleteResponse(BaseModel):
    id: Optional[str] = None
    """The ID of the deleted resource."""

    deleted_at: Optional[str] = None
    """The timestamp when the resource was deleted."""

    message: Optional[str] = None
