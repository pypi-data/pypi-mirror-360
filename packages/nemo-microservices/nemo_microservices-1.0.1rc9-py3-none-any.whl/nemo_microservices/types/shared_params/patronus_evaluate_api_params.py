# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

from ..shared.patronus_evaluation_success_strategy import PatronusEvaluationSuccessStrategy

__all__ = ["PatronusEvaluateAPIParams"]


class PatronusEvaluateAPIParams(TypedDict, total=False):
    params: object
    """Parameters to the Patronus Evaluate API"""

    success_strategy: PatronusEvaluationSuccessStrategy
    """
    Strategy for determining whether a Patronus Evaluation API request should pass,
    especially when multiple evaluators are called in a single request. ALL_PASS
    requires all evaluators to pass for success. ANY_PASS requires only one
    evaluator to pass for success.
    """
