# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

from .model_sort_field import ModelSortField
from .model_filter_param import ModelFilterParam

__all__ = ["ModelListParams"]


class ModelListParams(TypedDict, total=False):
    filter: ModelFilterParam
    """Filter models on various criteria.

    Where it makes sense, you can also filter on the existence of a property. For
    example:

    - `?filter[peft]=true`: would filter all models with `peft` attribute set.
    """

    page: int
    """Page number."""

    page_size: int
    """Page size."""

    sort: ModelSortField
    """The field to sort by.

    To sort in decreasing order, use `-` in front of the field name.
    """
