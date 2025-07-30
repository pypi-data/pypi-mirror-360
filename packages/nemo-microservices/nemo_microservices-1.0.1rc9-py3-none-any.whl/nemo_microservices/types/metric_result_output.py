# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, Optional

from .score import Score
from .._models import BaseModel

__all__ = ["MetricResultOutput"]


class MetricResultOutput(BaseModel):
    scores: Optional[Dict[str, Score]] = None
    """The value for all the scores computed for the metric."""
