# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

from ..shared.generic_sort_field import GenericSortField
from .model_deployment_filter_param import ModelDeploymentFilterParam

__all__ = ["ModelDeploymentListParams"]


class ModelDeploymentListParams(TypedDict, total=False):
    filter: ModelDeploymentFilterParam
    """Filter model_deployments on various criteria."""

    page: int
    """Page number."""

    page_size: int
    """Page size."""

    sort: GenericSortField
    """The field to sort by.

    To sort in decreasing order, use `-` in front of the field name.
    """
