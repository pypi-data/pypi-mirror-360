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

from typing_extensions import Required, TypedDict

from .training_type import TrainingType
from .shared.finetuning_type import FinetuningType

__all__ = ["CustomizationTrainingOptionParam"]


class CustomizationTrainingOptionParam(TypedDict, total=False):
    finetuning_type: Required[FinetuningType]

    micro_batch_size: Required[int]
    """The number of examples per data-parallel rank.

    More details at:
    https://docs.nvidia.com/deeplearning/nemo/user-guide/docs/en/main/nlp/nemo_megatron/batching.html
    """

    num_gpus: Required[int]
    """The number of GPUs per node to use for the specified training"""

    training_type: Required[TrainingType]

    data_parallel_size: int
    """
    Number of model replicas that process different data batches in parallel, with
    gradient synchronization across GPUs. Only available on HF checkpoint models.
    data_parallel_size _ tensor_parallel_size must equal num_gpus _ num_nodes
    """

    num_nodes: int
    """The number of nodes to use for the specified training"""

    pipeline_parallel_size: int
    """
    Number of GPUs used to split the model across layers for pipeline model
    parallelism (inter-layer). Only available on NeMo 2 checkpoint models.
    pipeline_parallel_size _ tensor_parallel_size must equal num_gpus _ num_nodes
    """

    tensor_parallel_size: int
    """
    Number of GPUs used to split individual layers for tensor model parallelism
    (intra-layer).
    """

    use_sequence_parallel: bool
    """If set, sequences are distributed over multiple GPUs"""
