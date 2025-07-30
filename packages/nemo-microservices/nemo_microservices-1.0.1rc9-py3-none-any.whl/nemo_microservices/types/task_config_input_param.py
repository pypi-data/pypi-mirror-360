# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Union
from typing_extensions import Required, TypeAlias, TypedDict

from .metric_config_param import MetricConfigParam
from .dataset_input_ev_param import DatasetInputEvParam

__all__ = ["TaskConfigInputParam", "Dataset"]

Dataset: TypeAlias = Union[str, DatasetInputEvParam]


class TaskConfigInputParam(TypedDict, total=False):
    type: Required[str]
    """The type of the task."""

    dataset: Dataset
    """
    Optional dataset reference.Typically, if not specified, means that the type of
    task has an implicit dataset.
    """

    metrics: Dict[str, MetricConfigParam]
    """Metrics to be computed for the task."""

    params: object
    """Additional parameters related to the task."""
