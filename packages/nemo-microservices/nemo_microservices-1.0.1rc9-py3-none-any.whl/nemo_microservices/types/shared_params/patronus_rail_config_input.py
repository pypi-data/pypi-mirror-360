# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

from .patronus_evaluate_config_input import PatronusEvaluateConfigInput

__all__ = ["PatronusRailConfigInput"]


class PatronusRailConfigInput(TypedDict, total=False):
    input: PatronusEvaluateConfigInput
    """Config for the Patronus Evaluate API call"""

    output: PatronusEvaluateConfigInput
    """Config for the Patronus Evaluate API call"""
