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

import httpx

from ..._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ..._utils import maybe_transform, async_maybe_transform
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ...pagination import SyncDefaultPagination, AsyncDefaultPagination
from ..._base_client import AsyncPaginator, make_request_options
from ...types.customization import (
    target_list_params,
    target_create_params,
    target_update_params,
)
from ...types.customization_target import CustomizationTarget
from ...types.shared.model_precision import ModelPrecision
from ...types.shared.generic_sort_field import GenericSortField
from ...types.customization.customization_target_filter_param import CustomizationTargetFilterParam

__all__ = ["TargetsResource", "AsyncTargetsResource"]


class TargetsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> TargetsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#accessing-raw-response-data-e-g-headers
        """
        return TargetsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> TargetsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#with_streaming_response
        """
        return TargetsResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        num_parameters: int,
        precision: ModelPrecision,
        base_model: str | NotGiven = NOT_GIVEN,
        description: str | NotGiven = NOT_GIVEN,
        enabled: bool | NotGiven = NOT_GIVEN,
        hf_endpoint: str | NotGiven = NOT_GIVEN,
        model_path: str | NotGiven = NOT_GIVEN,
        model_uri: str | NotGiven = NOT_GIVEN,
        name: str | NotGiven = NOT_GIVEN,
        namespace: str | NotGiven = NOT_GIVEN,
        project: str | NotGiven = NOT_GIVEN,
        tokenizer: object | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CustomizationTarget:
        """
        Create a new customization target.

        Args:
          num_parameters: Number of parameters used for training the model

          precision: Type of model precision.

              ## Values

              - `"int8"` - 8-bit integer precision
              - `"bf16"` - Brain floating point precision
              - `"fp16"` - 16-bit floating point precision
              - `"fp32"` - 32-bit floating point precision
              - `"fp8-mixed"` - Mixed 8-bit floating point precision available on Hopper and
                later architectures.
              - `"bf16-mixed"` - Mixed Brain floating point precision

          base_model: Default to being the same as the the configuration entry name, maps to the name
              in NIM

          description: The description of the entity.

          enabled: Enable the model for training jobs

          hf_endpoint: Configure the Hub base URL. Defaults to NeMo Data Store. Set value as
              "https://huggingface.co" to download model_uri from HuggingFace.

          model_path: Path to the model checkpoints to use for training. Absolute path or local path
              from the models cache

          model_uri: The URI of the model to download to the model cache at the model_path directory.
              To download from NGC, specify ngc://org/optional-team/model-name:version. To
              download from Nemo Data Store, specify hf://namespace/model-name@checkpoint-name

          name: The name of the entity. Must be unique inside the namespace. If not specified,
              it will be the same as the automatically generated id.

          namespace: The namespace of the entity. You can omit this field for namespace entities or
              in deployments that don't use namespaces.

          project: The URN of the project associated with this entity.

          tokenizer: Overrides for the model tokenizer

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/v1/customization/targets",
            body=maybe_transform(
                {
                    "num_parameters": num_parameters,
                    "precision": precision,
                    "base_model": base_model,
                    "description": description,
                    "enabled": enabled,
                    "hf_endpoint": hf_endpoint,
                    "model_path": model_path,
                    "model_uri": model_uri,
                    "name": name,
                    "namespace": namespace,
                    "project": project,
                    "tokenizer": tokenizer,
                },
                target_create_params.TargetCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CustomizationTarget,
        )

    def retrieve(
        self,
        target_name: str,
        *,
        namespace: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CustomizationTarget:
        """
        Get info about a customization target.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not namespace:
            raise ValueError(f"Expected a non-empty value for `namespace` but received {namespace!r}")
        if not target_name:
            raise ValueError(f"Expected a non-empty value for `target_name` but received {target_name!r}")
        return self._get(
            f"/v1/customization/targets/{namespace}/{target_name}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CustomizationTarget,
        )

    def update(
        self,
        target_name: str,
        *,
        namespace: str,
        base_model: str | NotGiven = NOT_GIVEN,
        description: str | NotGiven = NOT_GIVEN,
        enabled: bool | NotGiven = NOT_GIVEN,
        hf_endpoint: str | NotGiven = NOT_GIVEN,
        model_path: str | NotGiven = NOT_GIVEN,
        model_uri: str | NotGiven = NOT_GIVEN,
        num_parameters: int | NotGiven = NOT_GIVEN,
        precision: ModelPrecision | NotGiven = NOT_GIVEN,
        project: str | NotGiven = NOT_GIVEN,
        tokenizer: object | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CustomizationTarget:
        """
        Update customization target.

        Args:
          base_model: Default to being the same as the the configuration entry name, maps to the name
              in NIM

          description: The description of the entity.

          enabled: Enable the model for training jobs

          hf_endpoint: Configure the Hub base URL. Defaults to NeMo Data Store. Set value as
              "https://huggingface.co" to download model_uri from HuggingFace.

          model_path: Path to the model checkpoints to use for training. Absolute path or local path
              from the models cache

          model_uri: The URI of the model to download to the model cache at the model_path directory.
              To download from NGC, specify ngc://org/optional-team/model-name:version. To
              download from Nemo Data Store, specify hf://namespace/model-name@checkpoint-name

          num_parameters: Number of parameters used for training the model

          precision: Type of model precision.

              ## Values

              - `"int8"` - 8-bit integer precision
              - `"bf16"` - Brain floating point precision
              - `"fp16"` - 16-bit floating point precision
              - `"fp32"` - 32-bit floating point precision
              - `"fp8-mixed"` - Mixed 8-bit floating point precision available on Hopper and
                later architectures.
              - `"bf16-mixed"` - Mixed Brain floating point precision

          project: The URN of the project associated with this entity.

          tokenizer: Overrides for the model tokenizer

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not namespace:
            raise ValueError(f"Expected a non-empty value for `namespace` but received {namespace!r}")
        if not target_name:
            raise ValueError(f"Expected a non-empty value for `target_name` but received {target_name!r}")
        return self._patch(
            f"/v1/customization/targets/{namespace}/{target_name}",
            body=maybe_transform(
                {
                    "base_model": base_model,
                    "description": description,
                    "enabled": enabled,
                    "hf_endpoint": hf_endpoint,
                    "model_path": model_path,
                    "model_uri": model_uri,
                    "num_parameters": num_parameters,
                    "precision": precision,
                    "project": project,
                    "tokenizer": tokenizer,
                },
                target_update_params.TargetUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CustomizationTarget,
        )

    def list(
        self,
        *,
        filter: CustomizationTargetFilterParam | NotGiven = NOT_GIVEN,
        page: int | NotGiven = NOT_GIVEN,
        page_size: int | NotGiven = NOT_GIVEN,
        sort: GenericSortField | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SyncDefaultPagination[CustomizationTarget]:
        """
        List available customization targets.

        Args:
          filter: Filter targets on various criteria.

          page: Page number.

          page_size: Page size.

          sort: The field to sort by. To sort in decreasing order, use `-` in front of the field
              name.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get_api_list(
            "/v1/customization/targets",
            page=SyncDefaultPagination[CustomizationTarget],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "filter": filter,
                        "page": page,
                        "page_size": page_size,
                        "sort": sort,
                    },
                    target_list_params.TargetListParams,
                ),
            ),
            model=CustomizationTarget,
        )

    def delete(
        self,
        target_name: str,
        *,
        namespace: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """Delete a customization target and its associated model files.

        First checks if
        any existing customization job is currently using the target. If not, target row
        is locked, and enabled is set to False, so that it cannot be used for creating a
        new customization job Once target is disabled, creates a k8s job to remove files
        from pvc and awaits until the k8s job is completed.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not namespace:
            raise ValueError(f"Expected a non-empty value for `namespace` but received {namespace!r}")
        if not target_name:
            raise ValueError(f"Expected a non-empty value for `target_name` but received {target_name!r}")
        return self._delete(
            f"/v1/customization/targets/{namespace}/{target_name}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )


class AsyncTargetsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncTargetsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#accessing-raw-response-data-e-g-headers
        """
        return AsyncTargetsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncTargetsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#with_streaming_response
        """
        return AsyncTargetsResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        num_parameters: int,
        precision: ModelPrecision,
        base_model: str | NotGiven = NOT_GIVEN,
        description: str | NotGiven = NOT_GIVEN,
        enabled: bool | NotGiven = NOT_GIVEN,
        hf_endpoint: str | NotGiven = NOT_GIVEN,
        model_path: str | NotGiven = NOT_GIVEN,
        model_uri: str | NotGiven = NOT_GIVEN,
        name: str | NotGiven = NOT_GIVEN,
        namespace: str | NotGiven = NOT_GIVEN,
        project: str | NotGiven = NOT_GIVEN,
        tokenizer: object | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CustomizationTarget:
        """
        Create a new customization target.

        Args:
          num_parameters: Number of parameters used for training the model

          precision: Type of model precision.

              ## Values

              - `"int8"` - 8-bit integer precision
              - `"bf16"` - Brain floating point precision
              - `"fp16"` - 16-bit floating point precision
              - `"fp32"` - 32-bit floating point precision
              - `"fp8-mixed"` - Mixed 8-bit floating point precision available on Hopper and
                later architectures.
              - `"bf16-mixed"` - Mixed Brain floating point precision

          base_model: Default to being the same as the the configuration entry name, maps to the name
              in NIM

          description: The description of the entity.

          enabled: Enable the model for training jobs

          hf_endpoint: Configure the Hub base URL. Defaults to NeMo Data Store. Set value as
              "https://huggingface.co" to download model_uri from HuggingFace.

          model_path: Path to the model checkpoints to use for training. Absolute path or local path
              from the models cache

          model_uri: The URI of the model to download to the model cache at the model_path directory.
              To download from NGC, specify ngc://org/optional-team/model-name:version. To
              download from Nemo Data Store, specify hf://namespace/model-name@checkpoint-name

          name: The name of the entity. Must be unique inside the namespace. If not specified,
              it will be the same as the automatically generated id.

          namespace: The namespace of the entity. You can omit this field for namespace entities or
              in deployments that don't use namespaces.

          project: The URN of the project associated with this entity.

          tokenizer: Overrides for the model tokenizer

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/v1/customization/targets",
            body=await async_maybe_transform(
                {
                    "num_parameters": num_parameters,
                    "precision": precision,
                    "base_model": base_model,
                    "description": description,
                    "enabled": enabled,
                    "hf_endpoint": hf_endpoint,
                    "model_path": model_path,
                    "model_uri": model_uri,
                    "name": name,
                    "namespace": namespace,
                    "project": project,
                    "tokenizer": tokenizer,
                },
                target_create_params.TargetCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CustomizationTarget,
        )

    async def retrieve(
        self,
        target_name: str,
        *,
        namespace: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CustomizationTarget:
        """
        Get info about a customization target.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not namespace:
            raise ValueError(f"Expected a non-empty value for `namespace` but received {namespace!r}")
        if not target_name:
            raise ValueError(f"Expected a non-empty value for `target_name` but received {target_name!r}")
        return await self._get(
            f"/v1/customization/targets/{namespace}/{target_name}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CustomizationTarget,
        )

    async def update(
        self,
        target_name: str,
        *,
        namespace: str,
        base_model: str | NotGiven = NOT_GIVEN,
        description: str | NotGiven = NOT_GIVEN,
        enabled: bool | NotGiven = NOT_GIVEN,
        hf_endpoint: str | NotGiven = NOT_GIVEN,
        model_path: str | NotGiven = NOT_GIVEN,
        model_uri: str | NotGiven = NOT_GIVEN,
        num_parameters: int | NotGiven = NOT_GIVEN,
        precision: ModelPrecision | NotGiven = NOT_GIVEN,
        project: str | NotGiven = NOT_GIVEN,
        tokenizer: object | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CustomizationTarget:
        """
        Update customization target.

        Args:
          base_model: Default to being the same as the the configuration entry name, maps to the name
              in NIM

          description: The description of the entity.

          enabled: Enable the model for training jobs

          hf_endpoint: Configure the Hub base URL. Defaults to NeMo Data Store. Set value as
              "https://huggingface.co" to download model_uri from HuggingFace.

          model_path: Path to the model checkpoints to use for training. Absolute path or local path
              from the models cache

          model_uri: The URI of the model to download to the model cache at the model_path directory.
              To download from NGC, specify ngc://org/optional-team/model-name:version. To
              download from Nemo Data Store, specify hf://namespace/model-name@checkpoint-name

          num_parameters: Number of parameters used for training the model

          precision: Type of model precision.

              ## Values

              - `"int8"` - 8-bit integer precision
              - `"bf16"` - Brain floating point precision
              - `"fp16"` - 16-bit floating point precision
              - `"fp32"` - 32-bit floating point precision
              - `"fp8-mixed"` - Mixed 8-bit floating point precision available on Hopper and
                later architectures.
              - `"bf16-mixed"` - Mixed Brain floating point precision

          project: The URN of the project associated with this entity.

          tokenizer: Overrides for the model tokenizer

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not namespace:
            raise ValueError(f"Expected a non-empty value for `namespace` but received {namespace!r}")
        if not target_name:
            raise ValueError(f"Expected a non-empty value for `target_name` but received {target_name!r}")
        return await self._patch(
            f"/v1/customization/targets/{namespace}/{target_name}",
            body=await async_maybe_transform(
                {
                    "base_model": base_model,
                    "description": description,
                    "enabled": enabled,
                    "hf_endpoint": hf_endpoint,
                    "model_path": model_path,
                    "model_uri": model_uri,
                    "num_parameters": num_parameters,
                    "precision": precision,
                    "project": project,
                    "tokenizer": tokenizer,
                },
                target_update_params.TargetUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CustomizationTarget,
        )

    def list(
        self,
        *,
        filter: CustomizationTargetFilterParam | NotGiven = NOT_GIVEN,
        page: int | NotGiven = NOT_GIVEN,
        page_size: int | NotGiven = NOT_GIVEN,
        sort: GenericSortField | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AsyncPaginator[CustomizationTarget, AsyncDefaultPagination[CustomizationTarget]]:
        """
        List available customization targets.

        Args:
          filter: Filter targets on various criteria.

          page: Page number.

          page_size: Page size.

          sort: The field to sort by. To sort in decreasing order, use `-` in front of the field
              name.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get_api_list(
            "/v1/customization/targets",
            page=AsyncDefaultPagination[CustomizationTarget],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "filter": filter,
                        "page": page,
                        "page_size": page_size,
                        "sort": sort,
                    },
                    target_list_params.TargetListParams,
                ),
            ),
            model=CustomizationTarget,
        )

    async def delete(
        self,
        target_name: str,
        *,
        namespace: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """Delete a customization target and its associated model files.

        First checks if
        any existing customization job is currently using the target. If not, target row
        is locked, and enabled is set to False, so that it cannot be used for creating a
        new customization job Once target is disabled, creates a k8s job to remove files
        from pvc and awaits until the k8s job is completed.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not namespace:
            raise ValueError(f"Expected a non-empty value for `namespace` but received {namespace!r}")
        if not target_name:
            raise ValueError(f"Expected a non-empty value for `target_name` but received {target_name!r}")
        return await self._delete(
            f"/v1/customization/targets/{namespace}/{target_name}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )


class TargetsResourceWithRawResponse:
    def __init__(self, targets: TargetsResource) -> None:
        self._targets = targets

        self.create = to_raw_response_wrapper(
            targets.create,
        )
        self.retrieve = to_raw_response_wrapper(
            targets.retrieve,
        )
        self.update = to_raw_response_wrapper(
            targets.update,
        )
        self.list = to_raw_response_wrapper(
            targets.list,
        )
        self.delete = to_raw_response_wrapper(
            targets.delete,
        )


class AsyncTargetsResourceWithRawResponse:
    def __init__(self, targets: AsyncTargetsResource) -> None:
        self._targets = targets

        self.create = async_to_raw_response_wrapper(
            targets.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            targets.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            targets.update,
        )
        self.list = async_to_raw_response_wrapper(
            targets.list,
        )
        self.delete = async_to_raw_response_wrapper(
            targets.delete,
        )


class TargetsResourceWithStreamingResponse:
    def __init__(self, targets: TargetsResource) -> None:
        self._targets = targets

        self.create = to_streamed_response_wrapper(
            targets.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            targets.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            targets.update,
        )
        self.list = to_streamed_response_wrapper(
            targets.list,
        )
        self.delete = to_streamed_response_wrapper(
            targets.delete,
        )


class AsyncTargetsResourceWithStreamingResponse:
    def __init__(self, targets: AsyncTargetsResource) -> None:
        self._targets = targets

        self.create = async_to_streamed_response_wrapper(
            targets.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            targets.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            targets.update,
        )
        self.list = async_to_streamed_response_wrapper(
            targets.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            targets.delete,
        )
