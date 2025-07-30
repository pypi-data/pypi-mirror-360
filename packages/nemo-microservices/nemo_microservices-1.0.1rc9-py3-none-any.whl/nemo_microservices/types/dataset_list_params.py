# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

from .dataset_sort_field import DatasetSortField
from .dataset_filter_param import DatasetFilterParam

__all__ = ["DatasetListParams"]


class DatasetListParams(TypedDict, total=False):
    filter: DatasetFilterParam
    """Filter configs on various criteria."""

    page: int
    """Page number."""

    page_size: int
    """Page size."""

    sort: DatasetSortField
    """The field to sort by.

    To sort in decreasing order, use `-` in front of the field name.
    """
