# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .._models import BaseModel

__all__ = ["MetricConfig"]


class MetricConfig(BaseModel):
    type: str
    """The type of the metric."""

    params: Optional[object] = None
    """Specific parameters for the metric."""
