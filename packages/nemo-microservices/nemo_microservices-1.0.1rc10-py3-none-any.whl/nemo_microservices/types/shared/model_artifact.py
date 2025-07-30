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
from .artifact_status import ArtifactStatus
from .model_precision import ModelPrecision
from .backend_engine_type import BackendEngineType

__all__ = ["ModelArtifact"]


class ModelArtifact(BaseModel):
    files_url: str
    """The location where the artifact files are stored."""

    status: ArtifactStatus
    """Model artifact status.

    ## Values

    - `"created"` - Artifact has been created
    - `"upload_failed"` - Artifact upload has failed
    - `"upload_completed"` - Artifact upload has completed successfully
    """

    backend_engine: Optional[BackendEngineType] = None
    """Type of backend engine.

    ## Values

    - `"nemo"` - NeMo framework engine
    - `"trt_llm"` - TensorRT-LLM engine
    - `"vllm"` - vLLM engine
    - `"faster_transformer"` - Faster Transformer engine
    - `"hugging_face"` - Hugging Face engine
    """

    gpu_arch: Optional[str] = None
    """The GPU architecture the model is optimized for."""

    precision: Optional[ModelPrecision] = None
    """Type of model precision.

    ## Values

    - `"int8"` - 8-bit integer precision
    - `"bf16"` - Brain floating point precision
    - `"fp16"` - 16-bit floating point precision
    - `"fp32"` - 32-bit floating point precision
    - `"fp8-mixed"` - Mixed 8-bit floating point precision available on Hopper and
      later architectures.
    - `"bf16-mixed"` - Mixed Brain floating point precision
    """

    tensor_parallelism: Optional[int] = None
    """
    The number of GPU devices to split and process the model's neural network
    layers.
    """
