# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ..._models import BaseModel
from .evaluation_job import EvaluationJob
from .evaluation_job_filter import EvaluationJobFilter
from ..shared.pagination_data import PaginationData

__all__ = ["EvaluationJobsPage"]


class EvaluationJobsPage(BaseModel):
    data: List[EvaluationJob]

    filter: Optional[EvaluationJobFilter] = None
    """Filtering information."""

    object: Optional[str] = None

    pagination: Optional[PaginationData] = None
    """Pagination information."""

    sort: Optional[str] = None
    """The field on which the results are sorted."""
