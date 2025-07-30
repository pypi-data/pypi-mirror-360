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

from typing import Optional

from ..._models import BaseModel
from ..training_type import TrainingType
from ..shared.job_status import JobStatus
from ..shared.finetuning_type import FinetuningType

__all__ = ["CustomizationJobListFilter"]


class CustomizationJobListFilter(BaseModel):
    base_model: Optional[str] = None
    """Filter by name of the base model."""

    batch_size: Optional[int] = None
    """
    Batch size is the number of training samples used to train a single forwardand
    backward pass.
    """

    dataset: Optional[str] = None
    """Filter by dataset files_url."""

    epochs: Optional[int] = None
    """Epochs is the number of complete passes through the training dataset."""

    finetuning_type: Optional[FinetuningType] = None
    """Filter by available finetuning types."""

    log_every_n_steps: Optional[int] = None
    """Control logging frequency for metrics tracking.

    It may slow down training to log on every single batch. By default, logs every
    10 training steps.
    """

    project: Optional[str] = None
    """Filter by project."""

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

    training_type: Optional[TrainingType] = None
    """Filter by training objective type."""
