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
from typing_extensions import Required, TypeAlias, TypedDict

from .guardrails_data_param import GuardrailsDataParam
from .shared_params.chat_completion_tool_message_param import ChatCompletionToolMessageParam
from .shared_params.chat_completion_user_message_param import ChatCompletionUserMessageParam
from .shared_params.chat_completion_system_message_param import ChatCompletionSystemMessageParam
from .shared_params.chat_completion_function_message_param import ChatCompletionFunctionMessageParam
from .shared_params.chat_completion_assistant_message_param import ChatCompletionAssistantMessageParam

__all__ = ["GuardrailCheckParams", "Message"]


class GuardrailCheckParams(TypedDict, total=False):
    messages: Required[Iterable[Message]]
    """A list of messages comprising the conversation so far"""

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

    response_format: Dict[str, str]
    """
    Format of the response, can be 'json_object' to force the model to output valid
    JSON.
    """

    seed: int
    """If specified, attempts to sample deterministically."""

    stop: Union[List[str], str]
    """Up to 4 sequences where the API will stop generating further tokens."""

    stream: bool
    """If set, partial message deltas will be sent, like in ChatGPT."""

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

    vision: bool
    """Whether this is a vision-capable request with image inputs."""


Message: TypeAlias = Union[
    ChatCompletionSystemMessageParam,
    ChatCompletionUserMessageParam,
    ChatCompletionAssistantMessageParam,
    ChatCompletionToolMessageParam,
    ChatCompletionFunctionMessageParam,
]
