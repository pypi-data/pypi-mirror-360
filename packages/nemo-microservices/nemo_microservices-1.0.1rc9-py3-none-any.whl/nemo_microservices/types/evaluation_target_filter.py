# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, Optional

from .._models import BaseModel
from .date_time_filter import DateTimeFilter

__all__ = ["EvaluationTargetFilter"]


class EvaluationTargetFilter(BaseModel):
    created_at: Optional[DateTimeFilter] = None
    """Filter by created_at date in ISO format."""

    custom_fields: Optional[Dict[str, str]] = None
    """A set of custom fields that the user can define and use for various purposes."""

    model: Optional[str] = None
    """Filter by target model."""

    name: Optional[str] = None
    """Filter by name of target."""

    namespace: Optional[str] = None
    """Filter by namespace."""

    project: Optional[str] = None
    """Filter by project."""

    type: Optional[str] = None
    """Filter by type of target."""
