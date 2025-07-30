# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ..._models import BaseModel
from .metric_keys import MetricKeys
from .metric_values import MetricValues

__all__ = ["CustomizationMetrics"]


class CustomizationMetrics(BaseModel):
    keys: Optional[List[MetricKeys]] = None
    """Metric keys"""

    metrics: Optional[MetricValues] = None
