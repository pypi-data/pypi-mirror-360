# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

from .function_parameters_param import FunctionParametersParam

__all__ = ["FunctionSchemaInputParam"]


class FunctionSchemaInputParam(TypedDict, total=False):
    description: Required[str]
    """Description of what the function does."""

    name: Required[str]
    """Name of the function."""

    parameters: Required[FunctionParametersParam]
    """Parameters schema for the function."""

    strict: bool
    """Whether the verification is in strict mode."""
