# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Union
from typing_extensions import Required, TypeAlias, TypedDict

__all__ = ["FunctionParameterParam"]


class FunctionParameterParamTyped(TypedDict, total=False):
    type: Required[str]
    """The type of the parameter provided."""

    description: str
    """The description of this parameter."""


FunctionParameterParam: TypeAlias = Union[FunctionParameterParamTyped, Dict[str, object]]
