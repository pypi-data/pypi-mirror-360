# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

from .patronus_evaluate_api_params import PatronusEvaluateAPIParams

__all__ = ["PatronusEvaluateConfigInput"]


class PatronusEvaluateConfigInput(TypedDict, total=False):
    evaluate_config: PatronusEvaluateAPIParams
    """Config to parameterize the Patronus Evaluate API call"""
