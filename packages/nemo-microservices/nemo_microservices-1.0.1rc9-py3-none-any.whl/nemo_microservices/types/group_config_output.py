# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Optional

from .._models import BaseModel
from .metric_config import MetricConfig

__all__ = ["GroupConfigOutput"]


class GroupConfigOutput(BaseModel):
    groups: Optional[object] = None
    """Subgroups for the current group."""

    metrics: Optional[Dict[str, MetricConfig]] = None
    """The metrics that should be computed for the group."""

    tasks: Optional[List[str]] = None
    """The names of the tasks that are part of the group."""
