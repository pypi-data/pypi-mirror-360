# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ..._models import BaseModel
from .evaluation_target import EvaluationTarget
from ..shared.pagination_data import PaginationData
from ..evaluation_target_filter import EvaluationTargetFilter

__all__ = ["EvaluationTargetsPage"]


class EvaluationTargetsPage(BaseModel):
    data: List[EvaluationTarget]

    filter: Optional[EvaluationTargetFilter] = None
    """Filtering information."""

    object: Optional[str] = None

    pagination: Optional[PaginationData] = None
    """Pagination information."""

    sort: Optional[str] = None
    """The field on which the results are sorted."""
