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

from typing import Union, Iterable
from typing_extensions import Required, Annotated, TypeAlias, TypedDict

from ..._utils import PropertyInfo
from .hyperparameters_param import HyperparametersParam
from .dataset_cu_param_param import DatasetCuParamParam
from ..shared_params.ownership import Ownership
from .dataset_parameters_param import DatasetParametersParam
from .wand_b_integration_param import WandBIntegrationParam
from ..customization_config_param import CustomizationConfigParam

__all__ = ["JobCreateParams", "Config", "Dataset"]


class JobCreateParams(TypedDict, total=False):
    config: Required[Config]
    """The customization configuration to be used."""

    dataset: Required[Dataset]
    """The dataset to be used for customization."""

    hyperparameters: Required[HyperparametersParam]
    """The hyperparameters to be used for customization."""

    dataset_parameters: DatasetParametersParam
    """Additional parameters to configure a dataset"""

    description: str
    """The description of the entity."""

    integrations: Iterable[WandBIntegrationParam]
    """A list of third party integrations for a job.

    Example: Weights & Biases integration.
    """

    name: str
    """The name of the entity.

    Must be unique inside the namespace. If not specified, it will be the same as
    the automatically generated id.
    """

    output_model: str
    """The output model.

    If not specified, no output model is created, only the artifact files written.
    """

    ownership: Ownership
    """Information about ownership of an entity.

    If the entity is a namespace, the `access_policies` will typically apply to all
    entities inside the namespace.
    """

    project: str
    """The URN of the project associated with this entity."""

    wandb_api_key: Annotated[str, PropertyInfo(alias="wandb-api-key")]


Config: TypeAlias = Union[str, CustomizationConfigParam]

Dataset: TypeAlias = Union[str, DatasetCuParamParam]
