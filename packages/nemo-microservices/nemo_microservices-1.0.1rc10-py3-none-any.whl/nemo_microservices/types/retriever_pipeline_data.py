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

from typing import Union, Optional
from typing_extensions import TypeAlias

from .._models import BaseModel
from .model_ev import ModelEv

__all__ = ["RetrieverPipelineData", "IndexEmbeddingModel", "QueryEmbeddingModel", "RerankerModel"]

IndexEmbeddingModel: TypeAlias = Union[str, ModelEv]

QueryEmbeddingModel: TypeAlias = Union[str, ModelEv]

RerankerModel: TypeAlias = Union[str, ModelEv]


class RetrieverPipelineData(BaseModel):
    index_embedding_model: IndexEmbeddingModel
    """The index embedding model."""

    query_embedding_model: QueryEmbeddingModel
    """The query embedding model."""

    reranker_model: Optional[RerankerModel] = None
    """The reranker model."""

    top_k: Optional[int] = None
    """The top k results to be used."""
