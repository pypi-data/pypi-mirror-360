# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, Union, Optional
from typing_extensions import TypeAlias

from .._models import BaseModel
from .dataset_ev import DatasetEv
from .metric_config import MetricConfig

__all__ = ["TaskConfigOutput", "Dataset"]

Dataset: TypeAlias = Union[str, DatasetEv]


class TaskConfigOutput(BaseModel):
    type: str
    """The type of the task."""

    dataset: Optional[Dataset] = None
    """
    Optional dataset reference.Typically, if not specified, means that the type of
    task has an implicit dataset.
    """

    metrics: Optional[Dict[str, MetricConfig]] = None
    """Metrics to be computed for the task."""

    params: Optional[object] = None
    """Additional parameters related to the task."""
