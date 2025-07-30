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

from typing import List, Union
from typing_extensions import TypedDict

from .generation_log_options_param import GenerationLogOptionsParam
from .generation_rails_options_param import GenerationRailsOptionsParam

__all__ = ["GenerationOptionsParam"]


class GenerationOptionsParam(TypedDict, total=False):
    llm_output: bool
    """Whether the response should also include any custom LLM output."""

    llm_params: object
    """Additional parameters that should be used for the LLM call"""

    log: GenerationLogOptionsParam
    """Options for what should be included in the generation log."""

    output_vars: Union[bool, List[str]]
    """Whether additional context information should be returned.

    When True is specified, the whole context is returned. Otherwise, a list of key
    names can be specified.
    """

    rails: GenerationRailsOptionsParam
    """Options for what rails should be used during the generation."""
