# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel

__all__ = ["CustomizationMetricValue"]


class CustomizationMetricValue(BaseModel):
    step: Optional[int] = None
    """The step the metric was reported (e.g., 23)."""

    timestamp: Optional[str] = None
    """Timestamp when the metric was reported"""

    value: Optional[float] = None
    """The metric value (e.g., 0.325)."""
