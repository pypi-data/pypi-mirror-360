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
from .sft_parameters import SftParameters
from .lora_parameters import LoraParameters
from .p_tuning_parameters import PTuningParameters
from ..shared.finetuning_type import FinetuningType
from .distillation_parameters import DistillationParameters

__all__ = ["Hyperparameters"]


class Hyperparameters(BaseModel):
    finetuning_type: FinetuningType
    """The finetuning type for the customization job."""

    batch_size: Optional[int] = None
    """
    Batch size is the number of training samples used to train a single forwardand
    backward pass.
    """

    distillation: Optional[DistillationParameters] = None
    """Specific parameters for knowledge distillation"""

    epochs: Optional[int] = None
    """Epochs is the number of complete passes through the training dataset."""

    learning_rate: Optional[float] = None
    """How much to adjust the model parameters in response to the loss gradient"""

    log_every_n_steps: Optional[int] = None
    """Control logging frequency for metrics tracking.

    It may slow down training to log on every single batch. By default, logs every
    10 training steps.
    """

    lora: Optional[LoraParameters] = None
    """Specific parameters for LoRA."""

    p_tuning: Optional[PTuningParameters] = None
    """Specific parameters for p-tuning."""

    sequence_packing_enabled: Optional[bool] = None
    """
    Sequence packing can improve speed of training by letting the training work on
    multiple rows at the same time. Experimental and not supported by all models. If
    a model is not supported, a warning will be returned in the response body and
    training will proceed with sequence packing disabled. Not recommended for
    produciton use. This flag may be removed in the future. See
    https://docs.nvidia.com/nemo-framework/user-guide/latest/sft_peft/packed_sequence.html
    for more details.
    """

    sft: Optional[SftParameters] = None
    """Specific parameters for SFT."""

    training_type: Optional[TrainingType] = None
    """The training type for the customization job."""

    val_check_interval: Optional[float] = None
    """
    Control how often to check the validation set with after a fixed number of
    training batches or pass a float in the range [0.1, 1.0] to check after a
    fraction of the training epoch. Note that Early Stopping monitors the validation
    loss and stops the training when no improvement is observed after 10 epochs with
    a minimum delta of 0.001. If val_check_interval is greater than the number of
    training batches, validation will run every epoch.
    """

    weight_decay: Optional[float] = None
    """
    An additional penalty term added to the gradient descent to keep weights low and
    mitigate overfitting.
    """
