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

from typing import Dict
from typing_extensions import Required, TypedDict

from .shared_params.ownership import Ownership

__all__ = ["DatasetUpdateParams"]


class DatasetUpdateParams(TypedDict, total=False):
    namespace: Required[str]

    custom_fields: Dict[str, str]
    """A set of custom fields that the user can define and use for various purposes."""

    description: str
    """The description of the entity."""

    files_url: str
    """The location where the artifact files are stored.

    This can be a URL pointing to NDS, Hugging Face, S3, or any other accessible
    resource location.
    """

    format: str
    """
    Specifies the dataset format, referring to the schema of the dataset rather than
    the file format. Examples include SQuAD, BEIR, etc.
    """

    hf_endpoint: str
    """For HuggingFace URLs, the endpoint that should be used.

    By default, this is set to the Data Store URL. For HuggingFace Hub, this should
    be set to "https://huggingface.co".
    """

    limit: int
    """The maximum number of items to be used from the dataset."""

    ownership: Ownership
    """Information about ownership of an entity.

    If the entity is a namespace, the `access_policies` will typically apply to all
    entities inside the namespace.
    """

    project: str
    """The URN of the project associated with this entity."""

    split: str
    """The split of the dataset. Examples include train, validation, test, etc."""
