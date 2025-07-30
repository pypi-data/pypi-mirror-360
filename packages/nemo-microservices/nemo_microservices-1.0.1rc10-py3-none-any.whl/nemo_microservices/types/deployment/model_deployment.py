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

from typing import List, Union, Optional
from datetime import datetime
from typing_extensions import TypeAlias

from ..._models import BaseModel
from ..shared.ownership import Ownership
from ..deployment_config import DeploymentConfig
from .model_deployment_status_details import ModelDeploymentStatusDetails

__all__ = ["ModelDeployment", "Config"]

Config: TypeAlias = Union[str, DeploymentConfig]


class ModelDeployment(BaseModel):
    config: Config
    """The deployment configuration."""

    status_details: ModelDeploymentStatusDetails
    """The status details of the deployment."""

    url: str
    """The URL of the deployment."""

    async_enabled: Optional[bool] = None
    """Whether the async mode is enabled."""

    created_at: Optional[datetime] = None
    """Timestamp for when the entity was created."""

    custom_fields: Optional[object] = None
    """A set of custom fields that the user can define and use for various purposes."""

    deployed: Optional[bool] = None
    """Whether the deployment is done."""

    description: Optional[str] = None
    """The description of the entity."""

    models: Optional[List[str]] = None
    """The models served by this deployment."""

    name: Optional[str] = None
    """The name of the identity.

    Must be unique inside the namespace. If not specified, it will be the same as
    the automatically generated id.
    """

    namespace: Optional[str] = None
    """The if of the namespace of the entity.

    This can be missing for namespace entities or in deployments that don't use
    namespaces.
    """

    ownership: Optional[Ownership] = None
    """Information about ownership of an entity.

    If the entity is a namespace, the `access_policies` will typically apply to all
    entities inside the namespace.
    """

    project: Optional[str] = None
    """The id of project associated with this entity."""

    schema_version: Optional[str] = None
    """The version of the schema for the object. Internal use only."""

    updated_at: Optional[datetime] = None
    """Timestamp for when the entity was last updated."""
