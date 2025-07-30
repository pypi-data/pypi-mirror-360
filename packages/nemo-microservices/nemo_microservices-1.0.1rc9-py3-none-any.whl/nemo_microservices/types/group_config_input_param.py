# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, List
from typing_extensions import TypedDict

from .metric_config_param import MetricConfigParam

__all__ = ["GroupConfigInputParam"]


class GroupConfigInputParam(TypedDict, total=False):
    groups: object
    """Subgroups for the current group."""

    metrics: Dict[str, MetricConfigParam]
    """The metrics that should be computed for the group."""

    tasks: List[str]
    """The names of the tasks that are part of the group."""
