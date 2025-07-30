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

from typing import Dict, Union
from typing_extensions import TypeAlias, TypedDict

from ..date_time_filter_param import DateTimeFilterParam
from ..evaluation_config_filter_param import EvaluationConfigFilterParam
from ..evaluation_target_filter_param import EvaluationTargetFilterParam

__all__ = ["EvaluationJobFilterParam", "Config", "Target"]

Config: TypeAlias = Union[str, EvaluationConfigFilterParam]

Target: TypeAlias = Union[str, EvaluationTargetFilterParam]


class EvaluationJobFilterParam(TypedDict, total=False):
    config: Config
    """Filter by config.

    It can be string of format {namespace}/{name} or entity of type
    EvaluationConfigFilter.
    """

    created_at: DateTimeFilterParam
    """Filter by created_at date in ISO format."""

    custom_fields: Dict[str, str]
    """A set of custom fields that the user can define and use for various purposes."""

    namespace: str
    """Filter by namespace."""

    project: str
    """Filter by project."""

    status: str
    """Filter by status of job."""

    target: Target
    """Filter by target.

    It can be string of format {namespace}/{name} or entity of type
    EvaluationTargetFilter.
    """
