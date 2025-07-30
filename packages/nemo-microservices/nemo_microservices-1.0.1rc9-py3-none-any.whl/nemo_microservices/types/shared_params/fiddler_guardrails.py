# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["FiddlerGuardrails"]


class FiddlerGuardrails(TypedDict, total=False):
    faithfulness_threshold: float
    """Fiddler Guardrails faithfulness detection threshold."""

    fiddler_endpoint: str
    """The global endpoint for Fiddler Guardrails requests."""

    safety_threshold: float
    """Fiddler Guardrails safety detection threshold."""
