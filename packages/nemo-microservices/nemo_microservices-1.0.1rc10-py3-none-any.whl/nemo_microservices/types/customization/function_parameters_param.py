# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
