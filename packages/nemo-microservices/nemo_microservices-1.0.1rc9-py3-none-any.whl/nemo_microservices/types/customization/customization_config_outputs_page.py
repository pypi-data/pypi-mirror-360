# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ..._models import BaseModel
from ..shared.pagination_data import PaginationData
from .customization_config_filter import CustomizationConfigFilter
from ..customization_config_output import CustomizationConfigOutput

__all__ = ["CustomizationConfigOutputsPage"]


class CustomizationConfigOutputsPage(BaseModel):
    data: List[CustomizationConfigOutput]

    filter: Optional[CustomizationConfigFilter] = None
    """Filtering information."""

    object: Optional[str] = None
    """The type of object being returned."""

    pagination: Optional[PaginationData] = None
    """Pagination information."""

    sort: Optional[str] = None
    """The field on which the results are sorted."""
