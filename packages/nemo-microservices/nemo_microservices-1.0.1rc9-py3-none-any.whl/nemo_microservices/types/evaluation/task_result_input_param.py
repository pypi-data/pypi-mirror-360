# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict
from typing_extensions import TypedDict

from .metric_result_input_param import MetricResultInputParam

__all__ = ["TaskResultInputParam"]


class TaskResultInputParam(TypedDict, total=False):
    metrics: Dict[str, MetricResultInputParam]
    """The value for all the metrics computed for the task."""
