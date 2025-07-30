# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

from .customization_config_sort_field import CustomizationConfigSortField
from .customization_config_filter_param import CustomizationConfigFilterParam

__all__ = ["ConfigListParams"]


class ConfigListParams(TypedDict, total=False):
    filter: CustomizationConfigFilterParam
    """Filter customization configs on various criteria."""

    page: int
    """Page number."""

    page_size: int
    """Page size."""

    sort: CustomizationConfigSortField
    """The field to sort by.

    To sort in decreasing order, use `-` in front of the field name.
    """
