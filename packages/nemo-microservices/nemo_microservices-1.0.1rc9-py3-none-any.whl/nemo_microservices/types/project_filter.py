# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .._models import BaseModel

__all__ = ["ProjectFilter"]


class ProjectFilter(BaseModel):
    name: Optional[str] = None
    """Filter by project name."""

    namespace: Optional[str] = None
    """Filter by namespace id."""
