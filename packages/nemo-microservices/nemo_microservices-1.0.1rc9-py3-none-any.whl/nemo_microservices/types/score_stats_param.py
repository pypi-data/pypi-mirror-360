# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["ScoreStatsParam"]


class ScoreStatsParam(TypedDict, total=False):
    count: int
    """The number of values used for computing the score."""

    max: float
    """The maximum of all values used for computing the score."""

    mean: float
    """The mean of all values used for computing the score."""

    min: float
    """The minimum of all values used for computing the score."""

    stddev: float
    """This is the population standard deviation, not the sample standard deviation.

            See https://towardsdatascience.com/variance-sample-vs-population-3ddbd29e498a
            for details.
    """

    stderr: float
    """The standard error."""

    sum: float
    """The sum of all values used for computing the score."""

    sum_squared: float
    """The sum of the square of all values used for computing the score."""

    variance: float
    """This is the population variance, not the sample variance.

            See https://towardsdatascience.com/variance-sample-vs-population-3ddbd29e498a
            for details.
    """
