# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ..._models import BaseModel
from .evaluation_config import EvaluationConfig
from ..shared.pagination_data import PaginationData
from ..evaluation_config_filter import EvaluationConfigFilter

__all__ = ["EvaluationConfigsPage"]


class EvaluationConfigsPage(BaseModel):
    data: List[EvaluationConfig]

    filter: Optional[EvaluationConfigFilter] = None
    """Filtering information."""

    object: Optional[str] = None

    pagination: Optional[PaginationData] = None
    """Pagination information."""

    sort: Optional[str] = None
    """The field on which the results are sorted."""
