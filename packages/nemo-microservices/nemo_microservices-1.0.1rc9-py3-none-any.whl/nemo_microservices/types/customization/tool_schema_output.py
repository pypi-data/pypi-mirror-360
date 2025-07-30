# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel
from .function_schema_output import FunctionSchemaOutput

__all__ = ["ToolSchemaOutput"]


class ToolSchemaOutput(BaseModel):
    function: FunctionSchemaOutput
    """Schema defining the function"""

    type: Optional[Literal["function"]] = None
    """Type of tool - currently only 'function' is supported"""
