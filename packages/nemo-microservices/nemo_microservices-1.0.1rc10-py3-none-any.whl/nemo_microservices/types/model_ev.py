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

from typing import Dict, List, Union, Optional
from datetime import datetime

from .._models import BaseModel
from .shared.ownership import Ownership
from .shared.model_spec import ModelSpec
from .shared.prompt_data import PromptData
from .shared.version_tag import VersionTag
from .shared.model_artifact import ModelArtifact
from .shared.guardrail_config import GuardrailConfig
from .shared.api_endpoint_data import APIEndpointData
from .shared.parameter_efficient_finetuning_data import ParameterEfficientFinetuningData

__all__ = ["ModelEv"]


class ModelEv(BaseModel):
    id: Optional[str] = None
    """The ID of the entity.

    With the exception of namespaces, this is always a semantically-prefixed
    base58-encoded uuid4 [<prefix>-base58(uuid4())].
    """

    api_endpoint: Optional[APIEndpointData] = None
    """Data about an API endpoint."""

    artifact: Optional[ModelArtifact] = None
    """
    Data about a model artifact (a set of checkpoint files, configs, and other
    auxiliary info).

    The `files_url` field can point to a DataStore location.

    Example:

    - nds://models/rdinu/my-lora-customization

    The `rdinu/my-lora-customization` part above is the actual repository.

    If a specific revision needs to be referred, the HuggingFace syntax is used.

    - nds://models/rdinu/my-lora-customization@v1
    - nds://models/rdinu/my-lora-customization@8df79a8
    """

    base_model: Union[str, object, None] = None
    """Link to another model which is used as a base for the current model."""

    created_at: Optional[datetime] = None
    """Timestamp for when the entity was created."""

    custom_fields: Optional[Dict[str, str]] = None
    """A set of custom fields that the user can define and use for various purposes."""

    description: Optional[str] = None
    """The description of the entity."""

    guardrails: Optional[GuardrailConfig] = None
    """A guardrail configuration"""

    name: Optional[str] = None
    """The name of the entity.

    Must be unique inside the namespace. If not specified, it will be the same as
    the automatically generated id.
    """

    namespace: Optional[str] = None
    """The namespace of the entity.

    This can be missing for namespace entities or in deployments that don't use
    namespaces.
    """

    ownership: Optional[Ownership] = None
    """Information about ownership of an entity.

    If the entity is a namespace, the `access_policies` will typically apply to all
    entities inside the namespace.
    """

    peft: Optional[ParameterEfficientFinetuningData] = None
    """Data about a parameter-efficient finetuning."""

    project: Optional[str] = None
    """The URN of the project associated with this entity."""

    prompt: Optional[PromptData] = None
    """Prompt engineering data."""

    schema_version: Optional[str] = None
    """The version of the schema for the object. Internal use only."""

    spec: Optional[ModelSpec] = None
    """Detailed specification about a model."""

    type_prefix: Optional[str] = None

    updated_at: Optional[datetime] = None
    """Timestamp for when the entity was last updated."""

    version_id: Optional[str] = None
    """A unique, immutable id for the version. This is similar to the commit hash."""

    version_tags: Optional[List[VersionTag]] = None
    """The list of version tags associated with this entity."""
