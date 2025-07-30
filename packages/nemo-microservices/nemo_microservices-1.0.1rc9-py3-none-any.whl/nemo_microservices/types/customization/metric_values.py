# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ..._models import BaseModel
from .customization_metric_value import CustomizationMetricValue

__all__ = ["MetricValues"]


class MetricValues(BaseModel):
    train_loss: Optional[List[CustomizationMetricValue]] = None

    val_loss: Optional[List[CustomizationMetricValue]] = None
