# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel

__all__ = ["AutoAlignOptions"]


class AutoAlignOptions(BaseModel):
    guardrails_config: Optional[object] = None
    """The guardrails configuration that is passed to the AutoAlign endpoint"""
