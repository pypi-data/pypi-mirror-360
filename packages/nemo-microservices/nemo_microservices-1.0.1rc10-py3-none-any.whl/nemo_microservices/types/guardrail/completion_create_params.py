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

from typing import Dict, List, Union, Iterable
from typing_extensions import Literal, Required, TypedDict

from ..guardrails_data_param import GuardrailsDataParam

__all__ = ["CompletionCreateParamsBase", "CompletionCreateParamsNonStreaming", "CompletionCreateParamsStreaming"]


class CompletionCreateParamsBase(TypedDict, total=False):
    model: Required[str]
    """The model to use for completion. Must be one of the available models."""

    best_of: int
    """Not supported.

    Generates best_of completions server-side and returns the "best" (the one with
    the highest log probability per token). Results cannot be streamed. When used
    with n, best_of controls the number of candidate completions and n specifies how
    many to return - best_of must be greater than n.
    """

    echo: bool
    """Not supported.

    If `echo` is true, the response will include the prompt and optionally its
    tokens ids and logprobs.
    """

    frequency_penalty: float
    """
    Positive values penalize new tokens based on their existing frequency in the
    text.
    """

    function_call: Union[str, object]
    """Not Supported.

    Deprecated in favor of tool_choice. 'none' means the model will not call a
    function and instead generates a message. 'auto' means the model can pick
    between generating a message or calling a function. Specifying a particular
    function via {'name': 'my_function'} forces the model to call that function.
    """

    guardrails: GuardrailsDataParam
    """Guardrails specific options for the request."""

    ignore_eos: bool
    """Ignore the eos when running"""

    logit_bias: Dict[str, float]
    """Not Supported.

    Modify the likelihood of specified tokens appearing in the completion.
    """

    logprobs: bool
    """Whether to return log probabilities of the output tokens or not.

    If true, returns the log probabilities of each output token returned in the
    content of message
    """

    max_tokens: int
    """The maximum number of tokens that can be generated in the chat completion."""

    n: int
    """How many chat completion choices to generate for each input message."""

    presence_penalty: float
    """
    Positive values penalize new tokens based on whether they appear in the text so
    far.
    """

    prompt: Union[Iterable[int], Iterable[Iterable[int]], str, List[str]]
    """User prompt or list of token ids."""

    response_format: Dict[str, str]
    """
    Format of the response, can be 'json_object' to force the model to output valid
    JSON.
    """

    seed: int
    """If specified, attempts to sample deterministically."""

    stop: Union[List[str], str]
    """Up to 4 sequences where the API will stop generating further tokens."""

    suffix: str
    """Not supported. If echo is set, the prompt is returned with the completion."""

    system_fingerprint: str
    """Represents the backend configuration that the model runs with.

    Used with seed for determinism.
    """

    temperature: float
    """What sampling temperature to use, between 0 and 2."""

    tool_choice: Union[str, object]
    """Not Supported.

    Favored over function_call. Controls which (if any) function is called by the
    model.
    """

    tools: List[str]
    """A list of tools the model may call."""

    top_logprobs: int
    """The number of most likely tokens to return at each token position."""

    top_p: float
    """An alternative to sampling with temperature, called nucleus sampling."""

    user: str
    """Not Supported. A unique identifier representing your end-user."""


class CompletionCreateParamsNonStreaming(CompletionCreateParamsBase, total=False):
    stream: Literal[False]
    """If set, partial message deltas will be sent, like in ChatGPT."""


class CompletionCreateParamsStreaming(CompletionCreateParamsBase):
    stream: Required[Literal[True]]
    """If set, partial message deltas will be sent, like in ChatGPT."""


CompletionCreateParams = Union[CompletionCreateParamsNonStreaming, CompletionCreateParamsStreaming]
