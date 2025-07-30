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

from typing import Dict, Union, Optional
from typing_extensions import TypeAlias

from ..._models import BaseModel
from ..date_time_filter import DateTimeFilter
from ..evaluation_config_filter import EvaluationConfigFilter
from ..evaluation_target_filter import EvaluationTargetFilter

__all__ = ["EvaluationJobFilter", "Config", "Target"]

Config: TypeAlias = Union[str, EvaluationConfigFilter]

Target: TypeAlias = Union[str, EvaluationTargetFilter]


class EvaluationJobFilter(BaseModel):
    config: Optional[Config] = None
    """Filter by config.

    It can be string of format {namespace}/{name} or entity of type
    EvaluationConfigFilter.
    """

    created_at: Optional[DateTimeFilter] = None
    """Filter by created_at date in ISO format."""

    custom_fields: Optional[Dict[str, str]] = None
    """A set of custom fields that the user can define and use for various purposes."""

    namespace: Optional[str] = None
    """Filter by namespace."""

    project: Optional[str] = None
    """Filter by project."""

    status: Optional[str] = None
    """Filter by status of job."""

    target: Optional[Target] = None
    """Filter by target.

    It can be string of format {namespace}/{name} or entity of type
    EvaluationTargetFilter.
    """
