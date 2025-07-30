# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

from .project_sort_field import ProjectSortField
from .project_filter_param import ProjectFilterParam

__all__ = ["ProjectListParams"]


class ProjectListParams(TypedDict, total=False):
    filter: ProjectFilterParam
    """Filter projects on various criteria."""

    page: int
    """Page number."""

    page_size: int
    """Page size."""

    sort: ProjectSortField
    """The field to sort by.

    To sort in decreasing order, use `-` in front of the field name.
    """
