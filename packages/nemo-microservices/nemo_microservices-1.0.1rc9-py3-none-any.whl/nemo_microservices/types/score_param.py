# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

from .score_stats_param import ScoreStatsParam

__all__ = ["ScoreParam"]


class ScoreParam(TypedDict, total=False):
    value: Required[float]

    stats: ScoreStatsParam
    """Stats for a score."""
