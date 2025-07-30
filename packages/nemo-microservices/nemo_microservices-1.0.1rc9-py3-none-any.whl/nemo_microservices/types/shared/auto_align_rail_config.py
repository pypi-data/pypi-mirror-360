# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel
from .auto_align_options import AutoAlignOptions

__all__ = ["AutoAlignRailConfig"]


class AutoAlignRailConfig(BaseModel):
    input: Optional[AutoAlignOptions] = None
    """List of guardrails that are activated"""

    output: Optional[AutoAlignOptions] = None
    """List of guardrails that are activated"""

    parameters: Optional[object] = None
