# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .._models import BaseModel
from .score_stats import ScoreStats

__all__ = ["Score"]


class Score(BaseModel):
    value: float

    stats: Optional[ScoreStats] = None
    """Stats for a score."""
