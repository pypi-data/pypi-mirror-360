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
from .dataset_cu import DatasetCu
from .job_warning import JobWarning
from .hyperparameters import Hyperparameters
from .dataset_cu_param import DatasetCuParam
from ..shared.ownership import Ownership
from ..shared.job_status import JobStatus
from .dataset_parameters import DatasetParameters
from .wand_b_integration import WandBIntegration
from ..customization_config import CustomizationConfig
from .customization_status_details import CustomizationStatusDetails
from .customization_config_job_value import CustomizationConfigJobValue

__all__ = ["CustomizationJob", "Config", "Dataset"]

Config: TypeAlias = Union[str, CustomizationConfig]

Dataset: TypeAlias = Union[str, DatasetCu, DatasetCuParam]


class CustomizationJob(BaseModel):
    config: Config
    """The customization configuration template used."""

    dataset: Dataset
    """The dataset to be used for customization."""

    hyperparameters: Hyperparameters
    """The hyperparameters to be used for customization."""

    id: Optional[str] = None
    """The ID of the entity.

    With the exception of namespaces, this is always a semantically-prefixed
    base58-encoded uuid4 [<prefix>-base58(uuid4())].
    """

    config_snapshot: Optional[CustomizationConfigJobValue] = None
    """Config object as a value for CustomizationJob.config in /v1/customization/jobs"""

    created_at: Optional[datetime] = None
    """Timestamp for when the entity was created."""

    dataset_parameters: Optional[DatasetParameters] = None
    """Additional parameters to configure a dataset."""

    description: Optional[str] = None
    """The description of the entity."""

    integrations: Optional[List[WandBIntegration]] = None
    """A list of third party integrations for a job.

    Example: Weights & Biases integration.
    """

    namespace: Optional[str] = None
    """The namespace of the entity.

    This can be missing for namespace entities or in deployments that don't use
    namespaces.
    """

    output_model: Optional[str] = None
    """The output model.

    If not specified, no output model is created, only the artifact files written.
    """

    ownership: Optional[Ownership] = None
    """Information about ownership of an entity.

    If the entity is a namespace, the `access_policies` will typically apply to all
    entities inside the namespace.
    """

    project: Optional[str] = None
    """The URN of the project associated with this entity."""

    status: Optional[JobStatus] = None
    """Normalized statuses for all jobs.

    - **CREATED**: The job is created, but not yet scheduled.
    - **PENDING**: The job is waiting for resource allocation.
    - **RUNNING**: The job is currently running.
    - **CANCELLING**: The job is being cancelled at the user's request.
    - **CANCELLED**: The job has been cancelled by the user.
    - **CANCELLING**: The job is being cancelled at the user's request.
    - **FAILED**: The job failed to execute and terminated.
    - **COMPLETED**: The job has completed successfully.
    - **READY**: The job is ready to be used.
    - **UNKNOWN**: The job status is unknown.
    """

    status_details: Optional[CustomizationStatusDetails] = None
    """Detailed information about the customization"""

    updated_at: Optional[datetime] = None
    """Timestamp for when the entity was last updated."""

    warnings: Optional[List[JobWarning]] = None
    """Warnings when creating a job."""
