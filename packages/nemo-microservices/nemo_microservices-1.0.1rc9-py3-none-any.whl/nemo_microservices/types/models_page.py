# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .._models import BaseModel
from .model_filter import ModelFilter
from .model_output import ModelOutput
from .shared.pagination_data import PaginationData

__all__ = ["ModelsPage"]


class ModelsPage(BaseModel):
    data: List[ModelOutput]

    filter: Optional[ModelFilter] = None
    """Filtering information."""

    object: Optional[str] = None

    pagination: Optional[PaginationData] = None
    """Pagination information."""

    sort: Optional[str] = None
    """The field on which the results are sorted."""
