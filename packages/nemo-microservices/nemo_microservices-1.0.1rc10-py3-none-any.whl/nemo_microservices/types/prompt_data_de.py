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

from .._models import BaseModel
from .shared.inference_params import InferenceParams

__all__ = ["PromptDataDe"]


class PromptDataDe(BaseModel):
    icl_few_shot_examples: Optional[str] = None
    """A string including a set of examples. These are pre-pended to the prompt."""

    inference_params: Optional[InferenceParams] = None
    """Parameters that influence the inference of a model."""

    system_prompt: Optional[str] = None
    """The system prompt that should be applied during inference."""

    system_prompt_template: Optional[str] = None
    """
    The template which will be used to compile the final prompt used for prompting
    the LLM. Currently supports only {{icl_few_shot_examples}}
    """
