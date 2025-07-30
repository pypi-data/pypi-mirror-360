# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ..._models import BaseModel
from ..shared.pagination_data import PaginationData
from .customization_job_output import CustomizationJobOutput
from .customization_job_list_filter import CustomizationJobListFilter

__all__ = ["CustomizationJobOutputsPage"]


class CustomizationJobOutputsPage(BaseModel):
    data: List[CustomizationJobOutput]

    filter: Optional[CustomizationJobListFilter] = None
    """Filtering information."""

    object: Optional[str] = None
    """The type of object being returned."""

    pagination: Optional[PaginationData] = None
    """Pagination information."""

    sort: Optional[str] = None
    """The field on which the results are sorted."""
