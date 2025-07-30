# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

from ..shared.generic_sort_field import GenericSortField
from ..evaluation_target_filter_param import EvaluationTargetFilterParam

__all__ = ["TargetListParams"]


class TargetListParams(TypedDict, total=False):
    filter: EvaluationTargetFilterParam
    """Filter targets on various criteria."""

    page: int
    """Page number."""

    page_size: int
    """Page size."""

    sort: GenericSortField
    """The field to sort by.

    To sort in decreasing order, use `-` in front of the field name.
    """
