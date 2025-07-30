# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import TypedDict

from .tool_schema_input_param import ToolSchemaInputParam

__all__ = ["DatasetParametersInputParam"]


class DatasetParametersInputParam(TypedDict, total=False):
    tools: Iterable[ToolSchemaInputParam]
    """A list of tools that are available for training with tool calling"""
