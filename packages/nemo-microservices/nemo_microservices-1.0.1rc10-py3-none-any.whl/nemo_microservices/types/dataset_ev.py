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

from typing import Dict, List, Optional
from datetime import datetime

from .._models import BaseModel
from .shared.ownership import Ownership
from .shared.version_tag import VersionTag

__all__ = ["DatasetEv"]


class DatasetEv(BaseModel):
    files_url: str
    """The location where the artifact files are stored.

    This can be a URL pointing to NDS, Hugging Face, S3, or any other accessible
    resource location.
    """

    id: Optional[str] = None
    """The ID of the entity.

    With the exception of namespaces, this is always a semantically-prefixed
    base58-encoded uuid4 [<prefix>-base58(uuid4())].
    """

    created_at: Optional[datetime] = None
    """Timestamp for when the entity was created."""

    custom_fields: Optional[Dict[str, str]] = None
    """A set of custom fields that the user can define and use for various purposes."""

    description: Optional[str] = None
    """The description of the entity."""

    format: Optional[str] = None
    """
    Specifies the dataset format, referring to the schema of the dataset rather than
    the file format. Examples include SQuAD, BEIR, etc.
    """

    hf_endpoint: Optional[str] = None
    """For HuggingFace URLs, the endpoint that should be used.

    By default, this is set to the Data Store URL. For HuggingFace Hub, this should
    be set to "https://huggingface.co".
    """

    limit: Optional[int] = None
    """The maximum number of items to be used from the dataset."""

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

    project: Optional[str] = None
    """The URN of the project associated with this entity."""

    schema_version: Optional[str] = None
    """The version of the schema for the object. Internal use only."""

    split: Optional[str] = None
    """The split of the dataset. Examples include train, validation, test, etc."""

    type_prefix: Optional[str] = None
    """The type prefix of the entity ID.

    If not specified, it will be inferred from the entity type name, but this will
    likely result in long prefixes.
    """

    updated_at: Optional[datetime] = None
    """Timestamp for when the entity was last updated."""

    version_id: Optional[str] = None
    """A unique, immutable id for the version. This is similar to the commit hash."""

    version_tags: Optional[List[VersionTag]] = None
    """The list of version tags associated with this entity."""
