# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict
from typing_extensions import TypedDict

from .date_time_filter_param import DateTimeFilterParam

__all__ = ["EvaluationTargetFilterParam"]


class EvaluationTargetFilterParam(TypedDict, total=False):
    created_at: DateTimeFilterParam
    """Filter by created_at date in ISO format."""

    custom_fields: Dict[str, str]
    """A set of custom fields that the user can define and use for various purposes."""

    model: str
    """Filter by target model."""

    name: str
    """Filter by name of target."""

    namespace: str
    """Filter by namespace."""

    project: str
    """Filter by project."""

    type: str
    """Filter by type of target."""
