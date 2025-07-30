# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict
from typing_extensions import TypedDict

from ..score_param import ScoreParam

__all__ = ["MetricResultInputParam"]


class MetricResultInputParam(TypedDict, total=False):
    scores: Dict[str, ScoreParam]
    """The value for all the scores computed for the metric."""
