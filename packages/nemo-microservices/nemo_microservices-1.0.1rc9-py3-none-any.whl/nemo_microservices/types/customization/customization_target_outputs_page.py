# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ..._models import BaseModel
from ..shared.pagination_data import PaginationData
from .customization_target_filter import CustomizationTargetFilter
from .customization_target_output import CustomizationTargetOutput

__all__ = ["CustomizationTargetOutputsPage"]


class CustomizationTargetOutputsPage(BaseModel):
    data: List[CustomizationTargetOutput]

    filter: Optional[CustomizationTargetFilter] = None
    """Filtering information."""

    object: Optional[str] = None
    """The type of object being returned."""

    pagination: Optional[PaginationData] = None
    """Pagination information."""

    sort: Optional[str] = None
    """The field on which the results are sorted."""
