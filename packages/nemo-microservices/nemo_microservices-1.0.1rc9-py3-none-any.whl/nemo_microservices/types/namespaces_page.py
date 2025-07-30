# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .._models import BaseModel
from .namespace import Namespace
from .shared.pagination_data import PaginationData

__all__ = ["NamespacesPage"]


class NamespacesPage(BaseModel):
    data: List[Namespace]

    filter: Optional[object] = None
    """Filtering information."""

    object: Optional[str] = None

    pagination: Optional[PaginationData] = None
    """Pagination information."""

    sort: Optional[str] = None
    """The field on which the results are sorted."""
