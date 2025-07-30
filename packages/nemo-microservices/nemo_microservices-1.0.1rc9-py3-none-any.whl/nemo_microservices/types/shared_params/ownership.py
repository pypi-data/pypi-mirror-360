# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict
from typing_extensions import TypedDict

__all__ = ["Ownership"]


class Ownership(TypedDict, total=False):
    access_policies: Dict[str, str]
    """
    A general object for capturing access policies which can be used by an external
    service to determine ACLs
    """

    created_by: str
    """The ID of the user that created this entity."""
