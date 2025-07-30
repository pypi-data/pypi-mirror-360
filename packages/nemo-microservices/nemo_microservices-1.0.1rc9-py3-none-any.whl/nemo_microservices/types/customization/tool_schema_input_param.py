# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

from .function_schema_input_param import FunctionSchemaInputParam

__all__ = ["ToolSchemaInputParam"]


class ToolSchemaInputParam(TypedDict, total=False):
    function: Required[FunctionSchemaInputParam]
    """Schema defining the function"""

    type: Literal["function"]
    """Type of tool - currently only 'function' is supported"""
