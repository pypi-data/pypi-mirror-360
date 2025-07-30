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

from typing import List, Optional
from datetime import datetime

from ..._models import BaseModel
from .status_log import StatusLog
from ..shared.job_status import JobStatus
from .customization_metrics import CustomizationMetrics

__all__ = ["CustomizationStatusDetails"]


class CustomizationStatusDetails(BaseModel):
    created_at: datetime
    """The time when training started."""

    status: JobStatus
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

    updated_at: datetime
    """The last time the status was updated."""

    best_epoch: Optional[int] = None
    """The epoch completed of the best checkpoint for the customized model"""

    elapsed_time: Optional[float] = None
    """Time in seconds that the job has been running/took to run."""

    epochs_completed: Optional[int] = None
    """The total number of epochs completed during training"""

    metrics: Optional[CustomizationMetrics] = None

    percentage_done: Optional[float] = None
    """Percentage tracking the training progress of the customization.

    The progress is calculated as the percentage of completed epochs divided by the
    total number of epochs multiplied by 100. The training progress may not be 100
    after training completes due to early stopping (validation loss did not improve
    significantly over time) or job time limit was reached.
    """

    status_logs: Optional[List[StatusLog]] = None
    """Detailed log for changes to the status of the customization job."""

    steps_completed: Optional[int] = None
    """The number of steps completed during training.

    The total number of steps is determined by hyperparameters, number of epochs and
    the batch size, and the number of samples in the training dataset.
    `total_steps = epochs * ceil(training_samples / batch_size)` when both training
    and validation datasets are used, or
    `total_steps = epochs * ceil(ceil(training_samples * 0.9) / batch_size)` when
    only training dataset is used.
    """

    steps_per_epoch: Optional[int] = None
    """The number of steps per epoch.

    Calculated as follows:
    `steps_per_epoch = ceil(training_samples / batch_size) / epochs`. If `null`,
    then Customizer simply doesn't know the value.
    """

    train_loss: Optional[float] = None
    """The training loss of the best checkpoint for the customized model"""

    val_loss: Optional[float] = None
    """The validation loss of the best checkpoint for the customized model"""
