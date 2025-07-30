# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, Optional

from ..._models import BaseModel

__all__ = ["Ownership"]


class Ownership(BaseModel):
    access_policies: Optional[Dict[str, str]] = None
    """
    A general object for capturing access policies which can be used by an external
    service to determine ACLs
    """

    created_by: Optional[str] = None
    """The ID of the user that created this entity."""
