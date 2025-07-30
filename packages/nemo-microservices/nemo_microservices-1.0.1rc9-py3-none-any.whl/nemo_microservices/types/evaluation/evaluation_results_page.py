# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ..._models import BaseModel
from ..evaluation_result import EvaluationResult
from ..shared.pagination_data import PaginationData
from .evaluation_result_filter import EvaluationResultFilter

__all__ = ["EvaluationResultsPage"]


class EvaluationResultsPage(BaseModel):
    data: List[EvaluationResult]

    filter: Optional[EvaluationResultFilter] = None
    """Filtering information."""

    object: Optional[str] = None

    pagination: Optional[PaginationData] = None
    """Pagination information."""

    sort: Optional[str] = None
    """The field on which the results are sorted."""
