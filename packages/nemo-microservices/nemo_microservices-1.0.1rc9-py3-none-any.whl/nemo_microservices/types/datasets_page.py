# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .dataset import Dataset
from .._models import BaseModel
from .dataset_filter import DatasetFilter
from .shared.pagination_data import PaginationData

__all__ = ["DatasetsPage"]


class DatasetsPage(BaseModel):
    data: List[Dataset]

    filter: Optional[DatasetFilter] = None
    """Filtering information."""

    object: Optional[str] = None

    pagination: Optional[PaginationData] = None
    """Pagination information."""

    sort: Optional[str] = None
    """The field on which the results are sorted."""
