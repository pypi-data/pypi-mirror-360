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
from typing_extensions import Literal, overload

import httpx

from ..types import completion_create_params
from .._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from .._utils import required_args, maybe_transform, async_maybe_transform
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._streaming import Stream, AsyncStream
from .._base_client import make_request_options
from ..types.completion_response import CompletionResponse
from ..types.completion_stream_response import CompletionStreamResponse

__all__ = ["CompletionsResource", "AsyncCompletionsResource"]


class CompletionsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> CompletionsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#accessing-raw-response-data-e-g-headers
        """
        return CompletionsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> CompletionsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#with_streaming_response
        """
        return CompletionsResourceWithStreamingResponse(self)

    @overload
    def create(
        self,
        *,
        model: str,
        best_of: int | NotGiven = NOT_GIVEN,
        echo: bool | NotGiven = NOT_GIVEN,
        frequency_penalty: float | NotGiven = NOT_GIVEN,
        function_call: Union[str, object] | NotGiven = NOT_GIVEN,
        ignore_eos: bool | NotGiven = NOT_GIVEN,
        logit_bias: Dict[str, float] | NotGiven = NOT_GIVEN,
        logprobs: bool | NotGiven = NOT_GIVEN,
        max_tokens: int | NotGiven = NOT_GIVEN,
        n: int | NotGiven = NOT_GIVEN,
        presence_penalty: float | NotGiven = NOT_GIVEN,
        prompt: Union[Iterable[int], Iterable[Iterable[int]], str, List[str]] | NotGiven = NOT_GIVEN,
        response_format: Dict[str, str] | NotGiven = NOT_GIVEN,
        seed: int | NotGiven = NOT_GIVEN,
        stop: Union[str, List[str]] | NotGiven = NOT_GIVEN,
        stream: Literal[False] | NotGiven = NOT_GIVEN,
        suffix: str | NotGiven = NOT_GIVEN,
        system_fingerprint: str | NotGiven = NOT_GIVEN,
        temperature: float | NotGiven = NOT_GIVEN,
        tool_choice: Union[str, object] | NotGiven = NOT_GIVEN,
        tools: List[str] | NotGiven = NOT_GIVEN,
        top_logprobs: int | NotGiven = NOT_GIVEN,
        top_p: float | NotGiven = NOT_GIVEN,
        user: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CompletionResponse:
        """
        Completion for the provided conversation.

        Args:
          model: The model to use for completion. Must be one of the available models.

          best_of: Not supported. Generates best_of completions server-side and returns the "best"
              (the one with the highest log probability per token). Results cannot be
              streamed. When used with n, best_of controls the number of candidate completions
              and n specifies how many to return - best_of must be greater than n.

          echo: Not supported. If `echo` is true, the response will include the prompt and
              optionally its tokens ids and logprobs.

          frequency_penalty: Positive values penalize new tokens based on their existing frequency in the
              text.

          function_call: Not Supported. Deprecated in favor of tool_choice. 'none' means the model will
              not call a function and instead generates a message. 'auto' means the model can
              pick between generating a message or calling a function. Specifying a particular
              function via {'name': 'my_function'} forces the model to call that function.

          ignore_eos: Ignore the eos when running

          logit_bias: Not Supported. Modify the likelihood of specified tokens appearing in the
              completion.

          logprobs: Whether to return log probabilities of the output tokens or not. If true,
              returns the log probabilities of each output token returned in the content of
              message

          max_tokens: The maximum number of tokens that can be generated in the chat completion.

          n: How many chat completion choices to generate for each input message.

          presence_penalty: Positive values penalize new tokens based on whether they appear in the text so
              far.

          prompt: User prompt or list of token ids.

          response_format: Format of the response, can be 'json_object' to force the model to output valid
              JSON.

          seed: If specified, attempts to sample deterministically.

          stop: Up to 4 sequences where the API will stop generating further tokens.

          stream: If set, partial message deltas will be sent, like in ChatGPT.

          suffix: Not supported. If echo is set, the prompt is returned with the completion.

          system_fingerprint: Represents the backend configuration that the model runs with. Used with seed
              for determinism.

          temperature: What sampling temperature to use, between 0 and 2.

          tool_choice: Not Supported. Favored over function_call. Controls which (if any) function is
              called by the model.

          tools: A list of tools the model may call.

          top_logprobs: The number of most likely tokens to return at each token position.

          top_p: An alternative to sampling with temperature, called nucleus sampling.

          user: Not Supported. A unique identifier representing your end-user.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    def create(
        self,
        *,
        model: str,
        stream: Literal[True],
        best_of: int | NotGiven = NOT_GIVEN,
        echo: bool | NotGiven = NOT_GIVEN,
        frequency_penalty: float | NotGiven = NOT_GIVEN,
        function_call: Union[str, object] | NotGiven = NOT_GIVEN,
        ignore_eos: bool | NotGiven = NOT_GIVEN,
        logit_bias: Dict[str, float] | NotGiven = NOT_GIVEN,
        logprobs: bool | NotGiven = NOT_GIVEN,
        max_tokens: int | NotGiven = NOT_GIVEN,
        n: int | NotGiven = NOT_GIVEN,
        presence_penalty: float | NotGiven = NOT_GIVEN,
        prompt: Union[Iterable[int], Iterable[Iterable[int]], str, List[str]] | NotGiven = NOT_GIVEN,
        response_format: Dict[str, str] | NotGiven = NOT_GIVEN,
        seed: int | NotGiven = NOT_GIVEN,
        stop: Union[str, List[str]] | NotGiven = NOT_GIVEN,
        suffix: str | NotGiven = NOT_GIVEN,
        system_fingerprint: str | NotGiven = NOT_GIVEN,
        temperature: float | NotGiven = NOT_GIVEN,
        tool_choice: Union[str, object] | NotGiven = NOT_GIVEN,
        tools: List[str] | NotGiven = NOT_GIVEN,
        top_logprobs: int | NotGiven = NOT_GIVEN,
        top_p: float | NotGiven = NOT_GIVEN,
        user: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Stream[CompletionStreamResponse]:
        """
        Completion for the provided conversation.

        Args:
          model: The model to use for completion. Must be one of the available models.

          stream: If set, partial message deltas will be sent, like in ChatGPT.

          best_of: Not supported. Generates best_of completions server-side and returns the "best"
              (the one with the highest log probability per token). Results cannot be
              streamed. When used with n, best_of controls the number of candidate completions
              and n specifies how many to return - best_of must be greater than n.

          echo: Not supported. If `echo` is true, the response will include the prompt and
              optionally its tokens ids and logprobs.

          frequency_penalty: Positive values penalize new tokens based on their existing frequency in the
              text.

          function_call: Not Supported. Deprecated in favor of tool_choice. 'none' means the model will
              not call a function and instead generates a message. 'auto' means the model can
              pick between generating a message or calling a function. Specifying a particular
              function via {'name': 'my_function'} forces the model to call that function.

          ignore_eos: Ignore the eos when running

          logit_bias: Not Supported. Modify the likelihood of specified tokens appearing in the
              completion.

          logprobs: Whether to return log probabilities of the output tokens or not. If true,
              returns the log probabilities of each output token returned in the content of
              message

          max_tokens: The maximum number of tokens that can be generated in the chat completion.

          n: How many chat completion choices to generate for each input message.

          presence_penalty: Positive values penalize new tokens based on whether they appear in the text so
              far.

          prompt: User prompt or list of token ids.

          response_format: Format of the response, can be 'json_object' to force the model to output valid
              JSON.

          seed: If specified, attempts to sample deterministically.

          stop: Up to 4 sequences where the API will stop generating further tokens.

          suffix: Not supported. If echo is set, the prompt is returned with the completion.

          system_fingerprint: Represents the backend configuration that the model runs with. Used with seed
              for determinism.

          temperature: What sampling temperature to use, between 0 and 2.

          tool_choice: Not Supported. Favored over function_call. Controls which (if any) function is
              called by the model.

          tools: A list of tools the model may call.

          top_logprobs: The number of most likely tokens to return at each token position.

          top_p: An alternative to sampling with temperature, called nucleus sampling.

          user: Not Supported. A unique identifier representing your end-user.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    def create(
        self,
        *,
        model: str,
        stream: bool,
        best_of: int | NotGiven = NOT_GIVEN,
        echo: bool | NotGiven = NOT_GIVEN,
        frequency_penalty: float | NotGiven = NOT_GIVEN,
        function_call: Union[str, object] | NotGiven = NOT_GIVEN,
        ignore_eos: bool | NotGiven = NOT_GIVEN,
        logit_bias: Dict[str, float] | NotGiven = NOT_GIVEN,
        logprobs: bool | NotGiven = NOT_GIVEN,
        max_tokens: int | NotGiven = NOT_GIVEN,
        n: int | NotGiven = NOT_GIVEN,
        presence_penalty: float | NotGiven = NOT_GIVEN,
        prompt: Union[Iterable[int], Iterable[Iterable[int]], str, List[str]] | NotGiven = NOT_GIVEN,
        response_format: Dict[str, str] | NotGiven = NOT_GIVEN,
        seed: int | NotGiven = NOT_GIVEN,
        stop: Union[str, List[str]] | NotGiven = NOT_GIVEN,
        suffix: str | NotGiven = NOT_GIVEN,
        system_fingerprint: str | NotGiven = NOT_GIVEN,
        temperature: float | NotGiven = NOT_GIVEN,
        tool_choice: Union[str, object] | NotGiven = NOT_GIVEN,
        tools: List[str] | NotGiven = NOT_GIVEN,
        top_logprobs: int | NotGiven = NOT_GIVEN,
        top_p: float | NotGiven = NOT_GIVEN,
        user: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CompletionResponse | Stream[CompletionStreamResponse]:
        """
        Completion for the provided conversation.

        Args:
          model: The model to use for completion. Must be one of the available models.

          stream: If set, partial message deltas will be sent, like in ChatGPT.

          best_of: Not supported. Generates best_of completions server-side and returns the "best"
              (the one with the highest log probability per token). Results cannot be
              streamed. When used with n, best_of controls the number of candidate completions
              and n specifies how many to return - best_of must be greater than n.

          echo: Not supported. If `echo` is true, the response will include the prompt and
              optionally its tokens ids and logprobs.

          frequency_penalty: Positive values penalize new tokens based on their existing frequency in the
              text.

          function_call: Not Supported. Deprecated in favor of tool_choice. 'none' means the model will
              not call a function and instead generates a message. 'auto' means the model can
              pick between generating a message or calling a function. Specifying a particular
              function via {'name': 'my_function'} forces the model to call that function.

          ignore_eos: Ignore the eos when running

          logit_bias: Not Supported. Modify the likelihood of specified tokens appearing in the
              completion.

          logprobs: Whether to return log probabilities of the output tokens or not. If true,
              returns the log probabilities of each output token returned in the content of
              message

          max_tokens: The maximum number of tokens that can be generated in the chat completion.

          n: How many chat completion choices to generate for each input message.

          presence_penalty: Positive values penalize new tokens based on whether they appear in the text so
              far.

          prompt: User prompt or list of token ids.

          response_format: Format of the response, can be 'json_object' to force the model to output valid
              JSON.

          seed: If specified, attempts to sample deterministically.

          stop: Up to 4 sequences where the API will stop generating further tokens.

          suffix: Not supported. If echo is set, the prompt is returned with the completion.

          system_fingerprint: Represents the backend configuration that the model runs with. Used with seed
              for determinism.

          temperature: What sampling temperature to use, between 0 and 2.

          tool_choice: Not Supported. Favored over function_call. Controls which (if any) function is
              called by the model.

          tools: A list of tools the model may call.

          top_logprobs: The number of most likely tokens to return at each token position.

          top_p: An alternative to sampling with temperature, called nucleus sampling.

          user: Not Supported. A unique identifier representing your end-user.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @required_args(["model"], ["model", "stream"])
    def create(
        self,
        *,
        model: str,
        best_of: int | NotGiven = NOT_GIVEN,
        echo: bool | NotGiven = NOT_GIVEN,
        frequency_penalty: float | NotGiven = NOT_GIVEN,
        function_call: Union[str, object] | NotGiven = NOT_GIVEN,
        ignore_eos: bool | NotGiven = NOT_GIVEN,
        logit_bias: Dict[str, float] | NotGiven = NOT_GIVEN,
        logprobs: bool | NotGiven = NOT_GIVEN,
        max_tokens: int | NotGiven = NOT_GIVEN,
        n: int | NotGiven = NOT_GIVEN,
        presence_penalty: float | NotGiven = NOT_GIVEN,
        prompt: Union[Iterable[int], Iterable[Iterable[int]], str, List[str]] | NotGiven = NOT_GIVEN,
        response_format: Dict[str, str] | NotGiven = NOT_GIVEN,
        seed: int | NotGiven = NOT_GIVEN,
        stop: Union[str, List[str]] | NotGiven = NOT_GIVEN,
        stream: Literal[False] | Literal[True] | NotGiven = NOT_GIVEN,
        suffix: str | NotGiven = NOT_GIVEN,
        system_fingerprint: str | NotGiven = NOT_GIVEN,
        temperature: float | NotGiven = NOT_GIVEN,
        tool_choice: Union[str, object] | NotGiven = NOT_GIVEN,
        tools: List[str] | NotGiven = NOT_GIVEN,
        top_logprobs: int | NotGiven = NOT_GIVEN,
        top_p: float | NotGiven = NOT_GIVEN,
        user: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CompletionResponse | Stream[CompletionStreamResponse]:
        return self._post(
            "/v1/completions",
            body=maybe_transform(
                {
                    "model": model,
                    "best_of": best_of,
                    "echo": echo,
                    "frequency_penalty": frequency_penalty,
                    "function_call": function_call,
                    "ignore_eos": ignore_eos,
                    "logit_bias": logit_bias,
                    "logprobs": logprobs,
                    "max_tokens": max_tokens,
                    "n": n,
                    "presence_penalty": presence_penalty,
                    "prompt": prompt,
                    "response_format": response_format,
                    "seed": seed,
                    "stop": stop,
                    "stream": stream,
                    "suffix": suffix,
                    "system_fingerprint": system_fingerprint,
                    "temperature": temperature,
                    "tool_choice": tool_choice,
                    "tools": tools,
                    "top_logprobs": top_logprobs,
                    "top_p": top_p,
                    "user": user,
                },
                completion_create_params.CompletionCreateParamsStreaming
                if stream
                else completion_create_params.CompletionCreateParamsNonStreaming,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CompletionResponse,
            stream=stream or False,
            stream_cls=Stream[CompletionStreamResponse],
        )


class AsyncCompletionsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncCompletionsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#accessing-raw-response-data-e-g-headers
        """
        return AsyncCompletionsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncCompletionsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#with_streaming_response
        """
        return AsyncCompletionsResourceWithStreamingResponse(self)

    @overload
    async def create(
        self,
        *,
        model: str,
        best_of: int | NotGiven = NOT_GIVEN,
        echo: bool | NotGiven = NOT_GIVEN,
        frequency_penalty: float | NotGiven = NOT_GIVEN,
        function_call: Union[str, object] | NotGiven = NOT_GIVEN,
        ignore_eos: bool | NotGiven = NOT_GIVEN,
        logit_bias: Dict[str, float] | NotGiven = NOT_GIVEN,
        logprobs: bool | NotGiven = NOT_GIVEN,
        max_tokens: int | NotGiven = NOT_GIVEN,
        n: int | NotGiven = NOT_GIVEN,
        presence_penalty: float | NotGiven = NOT_GIVEN,
        prompt: Union[Iterable[int], Iterable[Iterable[int]], str, List[str]] | NotGiven = NOT_GIVEN,
        response_format: Dict[str, str] | NotGiven = NOT_GIVEN,
        seed: int | NotGiven = NOT_GIVEN,
        stop: Union[str, List[str]] | NotGiven = NOT_GIVEN,
        stream: Literal[False] | NotGiven = NOT_GIVEN,
        suffix: str | NotGiven = NOT_GIVEN,
        system_fingerprint: str | NotGiven = NOT_GIVEN,
        temperature: float | NotGiven = NOT_GIVEN,
        tool_choice: Union[str, object] | NotGiven = NOT_GIVEN,
        tools: List[str] | NotGiven = NOT_GIVEN,
        top_logprobs: int | NotGiven = NOT_GIVEN,
        top_p: float | NotGiven = NOT_GIVEN,
        user: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CompletionResponse:
        """
        Completion for the provided conversation.

        Args:
          model: The model to use for completion. Must be one of the available models.

          best_of: Not supported. Generates best_of completions server-side and returns the "best"
              (the one with the highest log probability per token). Results cannot be
              streamed. When used with n, best_of controls the number of candidate completions
              and n specifies how many to return - best_of must be greater than n.

          echo: Not supported. If `echo` is true, the response will include the prompt and
              optionally its tokens ids and logprobs.

          frequency_penalty: Positive values penalize new tokens based on their existing frequency in the
              text.

          function_call: Not Supported. Deprecated in favor of tool_choice. 'none' means the model will
              not call a function and instead generates a message. 'auto' means the model can
              pick between generating a message or calling a function. Specifying a particular
              function via {'name': 'my_function'} forces the model to call that function.

          ignore_eos: Ignore the eos when running

          logit_bias: Not Supported. Modify the likelihood of specified tokens appearing in the
              completion.

          logprobs: Whether to return log probabilities of the output tokens or not. If true,
              returns the log probabilities of each output token returned in the content of
              message

          max_tokens: The maximum number of tokens that can be generated in the chat completion.

          n: How many chat completion choices to generate for each input message.

          presence_penalty: Positive values penalize new tokens based on whether they appear in the text so
              far.

          prompt: User prompt or list of token ids.

          response_format: Format of the response, can be 'json_object' to force the model to output valid
              JSON.

          seed: If specified, attempts to sample deterministically.

          stop: Up to 4 sequences where the API will stop generating further tokens.

          stream: If set, partial message deltas will be sent, like in ChatGPT.

          suffix: Not supported. If echo is set, the prompt is returned with the completion.

          system_fingerprint: Represents the backend configuration that the model runs with. Used with seed
              for determinism.

          temperature: What sampling temperature to use, between 0 and 2.

          tool_choice: Not Supported. Favored over function_call. Controls which (if any) function is
              called by the model.

          tools: A list of tools the model may call.

          top_logprobs: The number of most likely tokens to return at each token position.

          top_p: An alternative to sampling with temperature, called nucleus sampling.

          user: Not Supported. A unique identifier representing your end-user.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    async def create(
        self,
        *,
        model: str,
        stream: Literal[True],
        best_of: int | NotGiven = NOT_GIVEN,
        echo: bool | NotGiven = NOT_GIVEN,
        frequency_penalty: float | NotGiven = NOT_GIVEN,
        function_call: Union[str, object] | NotGiven = NOT_GIVEN,
        ignore_eos: bool | NotGiven = NOT_GIVEN,
        logit_bias: Dict[str, float] | NotGiven = NOT_GIVEN,
        logprobs: bool | NotGiven = NOT_GIVEN,
        max_tokens: int | NotGiven = NOT_GIVEN,
        n: int | NotGiven = NOT_GIVEN,
        presence_penalty: float | NotGiven = NOT_GIVEN,
        prompt: Union[Iterable[int], Iterable[Iterable[int]], str, List[str]] | NotGiven = NOT_GIVEN,
        response_format: Dict[str, str] | NotGiven = NOT_GIVEN,
        seed: int | NotGiven = NOT_GIVEN,
        stop: Union[str, List[str]] | NotGiven = NOT_GIVEN,
        suffix: str | NotGiven = NOT_GIVEN,
        system_fingerprint: str | NotGiven = NOT_GIVEN,
        temperature: float | NotGiven = NOT_GIVEN,
        tool_choice: Union[str, object] | NotGiven = NOT_GIVEN,
        tools: List[str] | NotGiven = NOT_GIVEN,
        top_logprobs: int | NotGiven = NOT_GIVEN,
        top_p: float | NotGiven = NOT_GIVEN,
        user: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AsyncStream[CompletionStreamResponse]:
        """
        Completion for the provided conversation.

        Args:
          model: The model to use for completion. Must be one of the available models.

          stream: If set, partial message deltas will be sent, like in ChatGPT.

          best_of: Not supported. Generates best_of completions server-side and returns the "best"
              (the one with the highest log probability per token). Results cannot be
              streamed. When used with n, best_of controls the number of candidate completions
              and n specifies how many to return - best_of must be greater than n.

          echo: Not supported. If `echo` is true, the response will include the prompt and
              optionally its tokens ids and logprobs.

          frequency_penalty: Positive values penalize new tokens based on their existing frequency in the
              text.

          function_call: Not Supported. Deprecated in favor of tool_choice. 'none' means the model will
              not call a function and instead generates a message. 'auto' means the model can
              pick between generating a message or calling a function. Specifying a particular
              function via {'name': 'my_function'} forces the model to call that function.

          ignore_eos: Ignore the eos when running

          logit_bias: Not Supported. Modify the likelihood of specified tokens appearing in the
              completion.

          logprobs: Whether to return log probabilities of the output tokens or not. If true,
              returns the log probabilities of each output token returned in the content of
              message

          max_tokens: The maximum number of tokens that can be generated in the chat completion.

          n: How many chat completion choices to generate for each input message.

          presence_penalty: Positive values penalize new tokens based on whether they appear in the text so
              far.

          prompt: User prompt or list of token ids.

          response_format: Format of the response, can be 'json_object' to force the model to output valid
              JSON.

          seed: If specified, attempts to sample deterministically.

          stop: Up to 4 sequences where the API will stop generating further tokens.

          suffix: Not supported. If echo is set, the prompt is returned with the completion.

          system_fingerprint: Represents the backend configuration that the model runs with. Used with seed
              for determinism.

          temperature: What sampling temperature to use, between 0 and 2.

          tool_choice: Not Supported. Favored over function_call. Controls which (if any) function is
              called by the model.

          tools: A list of tools the model may call.

          top_logprobs: The number of most likely tokens to return at each token position.

          top_p: An alternative to sampling with temperature, called nucleus sampling.

          user: Not Supported. A unique identifier representing your end-user.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    async def create(
        self,
        *,
        model: str,
        stream: bool,
        best_of: int | NotGiven = NOT_GIVEN,
        echo: bool | NotGiven = NOT_GIVEN,
        frequency_penalty: float | NotGiven = NOT_GIVEN,
        function_call: Union[str, object] | NotGiven = NOT_GIVEN,
        ignore_eos: bool | NotGiven = NOT_GIVEN,
        logit_bias: Dict[str, float] | NotGiven = NOT_GIVEN,
        logprobs: bool | NotGiven = NOT_GIVEN,
        max_tokens: int | NotGiven = NOT_GIVEN,
        n: int | NotGiven = NOT_GIVEN,
        presence_penalty: float | NotGiven = NOT_GIVEN,
        prompt: Union[Iterable[int], Iterable[Iterable[int]], str, List[str]] | NotGiven = NOT_GIVEN,
        response_format: Dict[str, str] | NotGiven = NOT_GIVEN,
        seed: int | NotGiven = NOT_GIVEN,
        stop: Union[str, List[str]] | NotGiven = NOT_GIVEN,
        suffix: str | NotGiven = NOT_GIVEN,
        system_fingerprint: str | NotGiven = NOT_GIVEN,
        temperature: float | NotGiven = NOT_GIVEN,
        tool_choice: Union[str, object] | NotGiven = NOT_GIVEN,
        tools: List[str] | NotGiven = NOT_GIVEN,
        top_logprobs: int | NotGiven = NOT_GIVEN,
        top_p: float | NotGiven = NOT_GIVEN,
        user: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CompletionResponse | AsyncStream[CompletionStreamResponse]:
        """
        Completion for the provided conversation.

        Args:
          model: The model to use for completion. Must be one of the available models.

          stream: If set, partial message deltas will be sent, like in ChatGPT.

          best_of: Not supported. Generates best_of completions server-side and returns the "best"
              (the one with the highest log probability per token). Results cannot be
              streamed. When used with n, best_of controls the number of candidate completions
              and n specifies how many to return - best_of must be greater than n.

          echo: Not supported. If `echo` is true, the response will include the prompt and
              optionally its tokens ids and logprobs.

          frequency_penalty: Positive values penalize new tokens based on their existing frequency in the
              text.

          function_call: Not Supported. Deprecated in favor of tool_choice. 'none' means the model will
              not call a function and instead generates a message. 'auto' means the model can
              pick between generating a message or calling a function. Specifying a particular
              function via {'name': 'my_function'} forces the model to call that function.

          ignore_eos: Ignore the eos when running

          logit_bias: Not Supported. Modify the likelihood of specified tokens appearing in the
              completion.

          logprobs: Whether to return log probabilities of the output tokens or not. If true,
              returns the log probabilities of each output token returned in the content of
              message

          max_tokens: The maximum number of tokens that can be generated in the chat completion.

          n: How many chat completion choices to generate for each input message.

          presence_penalty: Positive values penalize new tokens based on whether they appear in the text so
              far.

          prompt: User prompt or list of token ids.

          response_format: Format of the response, can be 'json_object' to force the model to output valid
              JSON.

          seed: If specified, attempts to sample deterministically.

          stop: Up to 4 sequences where the API will stop generating further tokens.

          suffix: Not supported. If echo is set, the prompt is returned with the completion.

          system_fingerprint: Represents the backend configuration that the model runs with. Used with seed
              for determinism.

          temperature: What sampling temperature to use, between 0 and 2.

          tool_choice: Not Supported. Favored over function_call. Controls which (if any) function is
              called by the model.

          tools: A list of tools the model may call.

          top_logprobs: The number of most likely tokens to return at each token position.

          top_p: An alternative to sampling with temperature, called nucleus sampling.

          user: Not Supported. A unique identifier representing your end-user.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @required_args(["model"], ["model", "stream"])
    async def create(
        self,
        *,
        model: str,
        best_of: int | NotGiven = NOT_GIVEN,
        echo: bool | NotGiven = NOT_GIVEN,
        frequency_penalty: float | NotGiven = NOT_GIVEN,
        function_call: Union[str, object] | NotGiven = NOT_GIVEN,
        ignore_eos: bool | NotGiven = NOT_GIVEN,
        logit_bias: Dict[str, float] | NotGiven = NOT_GIVEN,
        logprobs: bool | NotGiven = NOT_GIVEN,
        max_tokens: int | NotGiven = NOT_GIVEN,
        n: int | NotGiven = NOT_GIVEN,
        presence_penalty: float | NotGiven = NOT_GIVEN,
        prompt: Union[Iterable[int], Iterable[Iterable[int]], str, List[str]] | NotGiven = NOT_GIVEN,
        response_format: Dict[str, str] | NotGiven = NOT_GIVEN,
        seed: int | NotGiven = NOT_GIVEN,
        stop: Union[str, List[str]] | NotGiven = NOT_GIVEN,
        stream: Literal[False] | Literal[True] | NotGiven = NOT_GIVEN,
        suffix: str | NotGiven = NOT_GIVEN,
        system_fingerprint: str | NotGiven = NOT_GIVEN,
        temperature: float | NotGiven = NOT_GIVEN,
        tool_choice: Union[str, object] | NotGiven = NOT_GIVEN,
        tools: List[str] | NotGiven = NOT_GIVEN,
        top_logprobs: int | NotGiven = NOT_GIVEN,
        top_p: float | NotGiven = NOT_GIVEN,
        user: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CompletionResponse | AsyncStream[CompletionStreamResponse]:
        return await self._post(
            "/v1/completions",
            body=await async_maybe_transform(
                {
                    "model": model,
                    "best_of": best_of,
                    "echo": echo,
                    "frequency_penalty": frequency_penalty,
                    "function_call": function_call,
                    "ignore_eos": ignore_eos,
                    "logit_bias": logit_bias,
                    "logprobs": logprobs,
                    "max_tokens": max_tokens,
                    "n": n,
                    "presence_penalty": presence_penalty,
                    "prompt": prompt,
                    "response_format": response_format,
                    "seed": seed,
                    "stop": stop,
                    "stream": stream,
                    "suffix": suffix,
                    "system_fingerprint": system_fingerprint,
                    "temperature": temperature,
                    "tool_choice": tool_choice,
                    "tools": tools,
                    "top_logprobs": top_logprobs,
                    "top_p": top_p,
                    "user": user,
                },
                completion_create_params.CompletionCreateParamsStreaming
                if stream
                else completion_create_params.CompletionCreateParamsNonStreaming,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CompletionResponse,
            stream=stream or False,
            stream_cls=AsyncStream[CompletionStreamResponse],
        )


class CompletionsResourceWithRawResponse:
    def __init__(self, completions: CompletionsResource) -> None:
        self._completions = completions

        self.create = to_raw_response_wrapper(
            completions.create,
        )


class AsyncCompletionsResourceWithRawResponse:
    def __init__(self, completions: AsyncCompletionsResource) -> None:
        self._completions = completions

        self.create = async_to_raw_response_wrapper(
            completions.create,
        )


class CompletionsResourceWithStreamingResponse:
    def __init__(self, completions: CompletionsResource) -> None:
        self._completions = completions

        self.create = to_streamed_response_wrapper(
            completions.create,
        )


class AsyncCompletionsResourceWithStreamingResponse:
    def __init__(self, completions: AsyncCompletionsResource) -> None:
        self._completions = completions

        self.create = async_to_streamed_response_wrapper(
            completions.create,
        )
