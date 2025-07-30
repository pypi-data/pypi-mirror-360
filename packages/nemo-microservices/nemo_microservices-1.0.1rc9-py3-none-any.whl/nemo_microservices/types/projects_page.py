# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .project import Project
from .._models import BaseModel
from .project_filter import ProjectFilter
from .shared.pagination_data import PaginationData

__all__ = ["ProjectsPage"]


class ProjectsPage(BaseModel):
    data: List[Project]

    filter: Optional[ProjectFilter] = None
    """Filtering information."""

    object: Optional[str] = None

    pagination: Optional[PaginationData] = None
    """Pagination information."""

    sort: Optional[str] = None
    """The field on which the results are sorted."""
