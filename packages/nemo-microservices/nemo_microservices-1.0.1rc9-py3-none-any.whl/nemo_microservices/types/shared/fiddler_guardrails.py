# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel

__all__ = ["FiddlerGuardrails"]


class FiddlerGuardrails(BaseModel):
    faithfulness_threshold: Optional[float] = None
    """Fiddler Guardrails faithfulness detection threshold."""

    fiddler_endpoint: Optional[str] = None
    """The global endpoint for Fiddler Guardrails requests."""

    safety_threshold: Optional[float] = None
    """Fiddler Guardrails safety detection threshold."""
