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

from .artifact_status_de import ArtifactStatusDe
from .model_precision_de import ModelPrecisionDe
from .backend_engine_type_de import BackendEngineTypeDe

__all__ = ["ModelArtifactDeParam"]


class ModelArtifactDeParam(TypedDict, total=False):
    files_url: Required[str]
    """The location where the artifact files are stored."""

    status: Required[ArtifactStatusDe]
    """The status of the model artifact."""

    backend_engine: BackendEngineTypeDe
    """Types of backend engine."""

    gpu_arch: str

    precision: ModelPrecisionDe
    """Types of model precision."""

    tensor_parallelism: int
