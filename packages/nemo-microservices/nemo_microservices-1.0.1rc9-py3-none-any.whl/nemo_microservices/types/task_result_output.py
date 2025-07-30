# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, Optional

from .._models import BaseModel
from .metric_result_output import MetricResultOutput

__all__ = ["TaskResultOutput"]


class TaskResultOutput(BaseModel):
    metrics: Optional[Dict[str, MetricResultOutput]] = None
    """The value for all the metrics computed for the task."""
