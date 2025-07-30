# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, List, Union
from typing_extensions import Literal, Annotated, TypeAlias, TypedDict

from ..._utils import PropertyInfo
from .function_parameter_param import FunctionParameterParam

__all__ = ["FunctionParametersParam"]


class FunctionParametersParamTyped(TypedDict, total=False):
    additional_properties: Annotated[bool, PropertyInfo(alias="additionalProperties")]
    """Additional properties are allowed."""

    properties: Dict[str, FunctionParameterParam]
    """Dictionary of parameter names to their type definitions."""

    required: List[str]
    """List of required parameter names."""

    type: Literal["object"]
    """Type of parameters - currently only 'object' is supported."""


FunctionParametersParam: TypeAlias = Union[FunctionParametersParamTyped, Dict[str, object]]
