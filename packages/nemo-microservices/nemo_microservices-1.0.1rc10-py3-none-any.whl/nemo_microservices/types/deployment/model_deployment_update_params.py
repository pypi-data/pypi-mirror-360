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
from typing_extensions import Required, TypeAlias, TypedDict

from ..deployment_config_param import DeploymentConfigParam
from ..shared_params.ownership import Ownership

__all__ = ["ModelDeploymentUpdateParams", "Config"]


class ModelDeploymentUpdateParams(TypedDict, total=False):
    namespace: Required[str]

    async_enabled: bool
    """Whether the async mode is enabled."""

    config: Config
    """The deployment configuration."""

    custom_fields: object
    """A set of custom fields that the user can define and use for various purposes."""

    description: str
    """The description of the entity."""

    models: List[str]
    """The models served by this deployment."""

    ownership: Ownership
    """Information about ownership of an entity.

    If the entity is a namespace, the `access_policies` will typically apply to all
    entities inside the namespace.
    """

    project: str
    """The id of project associated with this entity."""

    schema_version: str
    """The version of the schema for the object. Internal use only."""


Config: TypeAlias = Union[str, DeploymentConfigParam]
