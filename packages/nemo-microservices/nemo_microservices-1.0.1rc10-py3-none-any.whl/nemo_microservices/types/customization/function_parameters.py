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

from typing import TYPE_CHECKING, Dict, List, Optional
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from ..._models import BaseModel
from .function_parameter import FunctionParameter

__all__ = ["FunctionParameters"]


class FunctionParameters(BaseModel):
    additional_properties: Optional[bool] = FieldInfo(alias="additionalProperties", default=None)
    """Additional properties are allowed."""

    properties: Optional[Dict[str, FunctionParameter]] = None
    """Dictionary of parameter names to their type definitions."""

    required: Optional[List[str]] = None
    """List of required parameter names."""

    type: Optional[Literal["object"]] = None
    """Type of parameters - currently only 'object' is supported."""

    if TYPE_CHECKING:
        # Stub to indicate that arbitrary properties are accepted.
        # To access properties that are not valid identifiers you can use `getattr`, e.g.
        # `getattr(obj, '$type')`
        def __getattr__(self, attr: str) -> object: ...
