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

from typing import Dict, Iterable

import httpx

from ...types import TrainingPodSpecParam
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
    CustomizationConfigSortField,
    config_list_params,
    config_create_params,
    config_update_params,
)
from ...types.customization_config import CustomizationConfig
from ...types.shared.model_precision import ModelPrecision
from ...types.shared_params.ownership import Ownership
from ...types.training_pod_spec_param import TrainingPodSpecParam
from ...types.customization_training_option_param import CustomizationTrainingOptionParam
from ...types.customization.customization_config_sort_field import CustomizationConfigSortField
from ...types.customization.customization_config_filter_param import CustomizationConfigFilterParam
from ...types.customization.customization_training_option_removal_param import CustomizationTrainingOptionRemovalParam

__all__ = ["ConfigsResource", "AsyncConfigsResource"]


class ConfigsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ConfigsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#accessing-raw-response-data-e-g-headers
        """
        return ConfigsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ConfigsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#with_streaming_response
        """
        return ConfigsResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        max_seq_length: int,
        training_options: Iterable[CustomizationTrainingOptionParam],
        chat_prompt_template: str | NotGiven = NOT_GIVEN,
        custom_fields: Dict[str, str] | NotGiven = NOT_GIVEN,
        dataset_schemas: Iterable[object] | NotGiven = NOT_GIVEN,
        description: str | NotGiven = NOT_GIVEN,
        name: str | NotGiven = NOT_GIVEN,
        namespace: str | NotGiven = NOT_GIVEN,
        ownership: Ownership | NotGiven = NOT_GIVEN,
        pod_spec: TrainingPodSpecParam | NotGiven = NOT_GIVEN,
        project: str | NotGiven = NOT_GIVEN,
        prompt_template: str | NotGiven = NOT_GIVEN,
        target: config_create_params.Target | NotGiven = NOT_GIVEN,
        training_precision: ModelPrecision | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CustomizationConfig:
        """
        Create a new customization config.

        Args:
          max_seq_length: The largest context used for training. Datasets are truncated based on the
              maximum sequence length.

          training_options: Resource configuration for each training option for the model.

          chat_prompt_template: Chat Prompt Template to apply to the model to make it compatible with chat
              datasets

          custom_fields: A set of custom fields that the user can define and use for various purposes.

          dataset_schemas: Descriptions of the expected formats of the datasets uploaded.

          description: The description of the entity.

          name: The name of the entity. Must be unique inside the namespace. If not specified,
              it will be the same as the automatically generated id.

          namespace: The namespace of the entity. This can be missing for namespace entities or in
              deployments that don't use namespaces.

          ownership: Information about ownership of an entity.

              If the entity is a namespace, the `access_policies` will typically apply to all
              entities inside the namespace.

          pod_spec: Additional parameters to ensure these training jobs get run on the appropriate
              hardware.

          project: The URN of the project associated with this entity.

          prompt_template: Prompt template used to extract keys from the dataset. E.g.
              prompt_template='{input} {output}', and sample looks like '{\"input\": \"Q: 2x2
              A:\", \"output\": \"4\"}' then the model sees 'Q: 2x2 A: 4'

          target: The target to perform the customization on

          training_precision: Type of model precision.

              ## Values

              - `"int8"` - 8-bit integer precision
              - `"bf16"` - Brain floating point precision
              - `"fp16"` - 16-bit floating point precision
              - `"fp32"` - 32-bit floating point precision
              - `"fp8-mixed"` - Mixed 8-bit floating point precision available on Hopper and
                later architectures.
              - `"bf16-mixed"` - Mixed Brain floating point precision

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/v1/customization/configs",
            body=maybe_transform(
                {
                    "max_seq_length": max_seq_length,
                    "training_options": training_options,
                    "chat_prompt_template": chat_prompt_template,
                    "custom_fields": custom_fields,
                    "dataset_schemas": dataset_schemas,
                    "description": description,
                    "name": name,
                    "namespace": namespace,
                    "ownership": ownership,
                    "pod_spec": pod_spec,
                    "project": project,
                    "prompt_template": prompt_template,
                    "target": target,
                    "training_precision": training_precision,
                },
                config_create_params.ConfigCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CustomizationConfig,
        )

    def retrieve(
        self,
        config_name: str,
        *,
        namespace: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CustomizationConfig:
        """
        Get Customization Config

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not namespace:
            raise ValueError(f"Expected a non-empty value for `namespace` but received {namespace!r}")
        if not config_name:
            raise ValueError(f"Expected a non-empty value for `config_name` but received {config_name!r}")
        return self._get(
            f"/v1/customization/configs/{namespace}/{config_name}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CustomizationConfig,
        )

    def update(
        self,
        config_name: str,
        *,
        namespace: str,
        add_training_options: Iterable[CustomizationTrainingOptionParam] | NotGiven = NOT_GIVEN,
        chat_prompt_template: str | NotGiven = NOT_GIVEN,
        custom_fields: Dict[str, str] | NotGiven = NOT_GIVEN,
        dataset_schemas: Iterable[object] | NotGiven = NOT_GIVEN,
        description: str | NotGiven = NOT_GIVEN,
        max_seq_length: int | NotGiven = NOT_GIVEN,
        ownership: Ownership | NotGiven = NOT_GIVEN,
        pod_spec: TrainingPodSpecParam | NotGiven = NOT_GIVEN,
        project: str | NotGiven = NOT_GIVEN,
        prompt_template: str | NotGiven = NOT_GIVEN,
        remove_training_options: Iterable[CustomizationTrainingOptionRemovalParam] | NotGiven = NOT_GIVEN,
        training_options: Iterable[CustomizationTrainingOptionParam] | NotGiven = NOT_GIVEN,
        training_precision: ModelPrecision | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CustomizationConfig:
        """
        Update a customization configuration with partial data.

        This endpoint supports partial updates with the following behavior:

        **Override Behavior (Complete Replacement):**

        - Top-level fields (e.g., description) - values are completely replaced
        - `pod_spec` - each field in the pod_spec is replaced if provided. If a field is
          not provided, it is not removed.
        - `dataset_schemas` - entire dataset schemas are replaced if provided, no
          merging is done

        **Training Options Management:** Training options are identified by the
        combination of `training_type` and `finetuning_type`. When updating training
        options:

        1. If `training_options` is provided, matching existing options are updated
           field-by-field
        2. If `add_training_options` is provided, new options are appended to the list
        3. If `remove_training_options` is provided, matching options are deleted
        4. All other existing training options remain unchanged

        Args:
          add_training_options: List of training options to add in the existing training options for the config.

          chat_prompt_template: Chat Prompt Template to apply to the model to make it compatible with chat
              datasets

          custom_fields: A set of custom fields that the user can define and use for various purposes.

          dataset_schemas: Descriptions of the expected formats of the datasets uploaded.

          description: The description of the entity.

          max_seq_length: The largest context used for training. Datasets are truncated based on the
              maximum sequence length.

          ownership: Information about ownership of an entity.

              If the entity is a namespace, the `access_policies` will typically apply to all
              entities inside the namespace.

          pod_spec: Additional parameters to ensure these training jobs get run on the appropriate
              hardware.

          project: The URN of the project associated with this entity.

          prompt_template: Prompt template used to extract keys from the dataset. E.g.
              prompt_template='{input} {output}', and sample looks like '{\"input\": \"Q: 2x2
              A:\", \"output\": \"4\"}' then the model sees 'Q: 2x2 A: 4'

          remove_training_options: List of training options to remove from the existing training options for the
              config.

          training_options: Resource configuration for each training option for the model.

          training_precision: Type of model precision.

              ## Values

              - `"int8"` - 8-bit integer precision
              - `"bf16"` - Brain floating point precision
              - `"fp16"` - 16-bit floating point precision
              - `"fp32"` - 32-bit floating point precision
              - `"fp8-mixed"` - Mixed 8-bit floating point precision available on Hopper and
                later architectures.
              - `"bf16-mixed"` - Mixed Brain floating point precision

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not namespace:
            raise ValueError(f"Expected a non-empty value for `namespace` but received {namespace!r}")
        if not config_name:
            raise ValueError(f"Expected a non-empty value for `config_name` but received {config_name!r}")
        return self._patch(
            f"/v1/customization/configs/{namespace}/{config_name}",
            body=maybe_transform(
                {
                    "add_training_options": add_training_options,
                    "chat_prompt_template": chat_prompt_template,
                    "custom_fields": custom_fields,
                    "dataset_schemas": dataset_schemas,
                    "description": description,
                    "max_seq_length": max_seq_length,
                    "ownership": ownership,
                    "pod_spec": pod_spec,
                    "project": project,
                    "prompt_template": prompt_template,
                    "remove_training_options": remove_training_options,
                    "training_options": training_options,
                    "training_precision": training_precision,
                },
                config_update_params.ConfigUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CustomizationConfig,
        )

    def list(
        self,
        *,
        filter: CustomizationConfigFilterParam | NotGiven = NOT_GIVEN,
        page: int | NotGiven = NOT_GIVEN,
        page_size: int | NotGiven = NOT_GIVEN,
        sort: CustomizationConfigSortField | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SyncDefaultPagination[CustomizationConfig]:
        """
        List available customization configs.

        Args:
          filter: Filter customization configs on various criteria.

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
            "/v1/customization/configs",
            page=SyncDefaultPagination[CustomizationConfig],
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
                    config_list_params.ConfigListParams,
                ),
            ),
            model=CustomizationConfig,
        )

    def delete(
        self,
        config_name: str,
        *,
        namespace: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """
        Delete Customization Config

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not namespace:
            raise ValueError(f"Expected a non-empty value for `namespace` but received {namespace!r}")
        if not config_name:
            raise ValueError(f"Expected a non-empty value for `config_name` but received {config_name!r}")
        return self._delete(
            f"/v1/customization/configs/{namespace}/{config_name}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )


class AsyncConfigsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncConfigsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#accessing-raw-response-data-e-g-headers
        """
        return AsyncConfigsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncConfigsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#with_streaming_response
        """
        return AsyncConfigsResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        max_seq_length: int,
        training_options: Iterable[CustomizationTrainingOptionParam],
        chat_prompt_template: str | NotGiven = NOT_GIVEN,
        custom_fields: Dict[str, str] | NotGiven = NOT_GIVEN,
        dataset_schemas: Iterable[object] | NotGiven = NOT_GIVEN,
        description: str | NotGiven = NOT_GIVEN,
        name: str | NotGiven = NOT_GIVEN,
        namespace: str | NotGiven = NOT_GIVEN,
        ownership: Ownership | NotGiven = NOT_GIVEN,
        pod_spec: TrainingPodSpecParam | NotGiven = NOT_GIVEN,
        project: str | NotGiven = NOT_GIVEN,
        prompt_template: str | NotGiven = NOT_GIVEN,
        target: config_create_params.Target | NotGiven = NOT_GIVEN,
        training_precision: ModelPrecision | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CustomizationConfig:
        """
        Create a new customization config.

        Args:
          max_seq_length: The largest context used for training. Datasets are truncated based on the
              maximum sequence length.

          training_options: Resource configuration for each training option for the model.

          chat_prompt_template: Chat Prompt Template to apply to the model to make it compatible with chat
              datasets

          custom_fields: A set of custom fields that the user can define and use for various purposes.

          dataset_schemas: Descriptions of the expected formats of the datasets uploaded.

          description: The description of the entity.

          name: The name of the entity. Must be unique inside the namespace. If not specified,
              it will be the same as the automatically generated id.

          namespace: The namespace of the entity. This can be missing for namespace entities or in
              deployments that don't use namespaces.

          ownership: Information about ownership of an entity.

              If the entity is a namespace, the `access_policies` will typically apply to all
              entities inside the namespace.

          pod_spec: Additional parameters to ensure these training jobs get run on the appropriate
              hardware.

          project: The URN of the project associated with this entity.

          prompt_template: Prompt template used to extract keys from the dataset. E.g.
              prompt_template='{input} {output}', and sample looks like '{\"input\": \"Q: 2x2
              A:\", \"output\": \"4\"}' then the model sees 'Q: 2x2 A: 4'

          target: The target to perform the customization on

          training_precision: Type of model precision.

              ## Values

              - `"int8"` - 8-bit integer precision
              - `"bf16"` - Brain floating point precision
              - `"fp16"` - 16-bit floating point precision
              - `"fp32"` - 32-bit floating point precision
              - `"fp8-mixed"` - Mixed 8-bit floating point precision available on Hopper and
                later architectures.
              - `"bf16-mixed"` - Mixed Brain floating point precision

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/v1/customization/configs",
            body=await async_maybe_transform(
                {
                    "max_seq_length": max_seq_length,
                    "training_options": training_options,
                    "chat_prompt_template": chat_prompt_template,
                    "custom_fields": custom_fields,
                    "dataset_schemas": dataset_schemas,
                    "description": description,
                    "name": name,
                    "namespace": namespace,
                    "ownership": ownership,
                    "pod_spec": pod_spec,
                    "project": project,
                    "prompt_template": prompt_template,
                    "target": target,
                    "training_precision": training_precision,
                },
                config_create_params.ConfigCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CustomizationConfig,
        )

    async def retrieve(
        self,
        config_name: str,
        *,
        namespace: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CustomizationConfig:
        """
        Get Customization Config

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not namespace:
            raise ValueError(f"Expected a non-empty value for `namespace` but received {namespace!r}")
        if not config_name:
            raise ValueError(f"Expected a non-empty value for `config_name` but received {config_name!r}")
        return await self._get(
            f"/v1/customization/configs/{namespace}/{config_name}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CustomizationConfig,
        )

    async def update(
        self,
        config_name: str,
        *,
        namespace: str,
        add_training_options: Iterable[CustomizationTrainingOptionParam] | NotGiven = NOT_GIVEN,
        chat_prompt_template: str | NotGiven = NOT_GIVEN,
        custom_fields: Dict[str, str] | NotGiven = NOT_GIVEN,
        dataset_schemas: Iterable[object] | NotGiven = NOT_GIVEN,
        description: str | NotGiven = NOT_GIVEN,
        max_seq_length: int | NotGiven = NOT_GIVEN,
        ownership: Ownership | NotGiven = NOT_GIVEN,
        pod_spec: TrainingPodSpecParam | NotGiven = NOT_GIVEN,
        project: str | NotGiven = NOT_GIVEN,
        prompt_template: str | NotGiven = NOT_GIVEN,
        remove_training_options: Iterable[CustomizationTrainingOptionRemovalParam] | NotGiven = NOT_GIVEN,
        training_options: Iterable[CustomizationTrainingOptionParam] | NotGiven = NOT_GIVEN,
        training_precision: ModelPrecision | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CustomizationConfig:
        """
        Update a customization configuration with partial data.

        This endpoint supports partial updates with the following behavior:

        **Override Behavior (Complete Replacement):**

        - Top-level fields (e.g., description) - values are completely replaced
        - `pod_spec` - each field in the pod_spec is replaced if provided. If a field is
          not provided, it is not removed.
        - `dataset_schemas` - entire dataset schemas are replaced if provided, no
          merging is done

        **Training Options Management:** Training options are identified by the
        combination of `training_type` and `finetuning_type`. When updating training
        options:

        1. If `training_options` is provided, matching existing options are updated
           field-by-field
        2. If `add_training_options` is provided, new options are appended to the list
        3. If `remove_training_options` is provided, matching options are deleted
        4. All other existing training options remain unchanged

        Args:
          add_training_options: List of training options to add in the existing training options for the config.

          chat_prompt_template: Chat Prompt Template to apply to the model to make it compatible with chat
              datasets

          custom_fields: A set of custom fields that the user can define and use for various purposes.

          dataset_schemas: Descriptions of the expected formats of the datasets uploaded.

          description: The description of the entity.

          max_seq_length: The largest context used for training. Datasets are truncated based on the
              maximum sequence length.

          ownership: Information about ownership of an entity.

              If the entity is a namespace, the `access_policies` will typically apply to all
              entities inside the namespace.

          pod_spec: Additional parameters to ensure these training jobs get run on the appropriate
              hardware.

          project: The URN of the project associated with this entity.

          prompt_template: Prompt template used to extract keys from the dataset. E.g.
              prompt_template='{input} {output}', and sample looks like '{\"input\": \"Q: 2x2
              A:\", \"output\": \"4\"}' then the model sees 'Q: 2x2 A: 4'

          remove_training_options: List of training options to remove from the existing training options for the
              config.

          training_options: Resource configuration for each training option for the model.

          training_precision: Type of model precision.

              ## Values

              - `"int8"` - 8-bit integer precision
              - `"bf16"` - Brain floating point precision
              - `"fp16"` - 16-bit floating point precision
              - `"fp32"` - 32-bit floating point precision
              - `"fp8-mixed"` - Mixed 8-bit floating point precision available on Hopper and
                later architectures.
              - `"bf16-mixed"` - Mixed Brain floating point precision

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not namespace:
            raise ValueError(f"Expected a non-empty value for `namespace` but received {namespace!r}")
        if not config_name:
            raise ValueError(f"Expected a non-empty value for `config_name` but received {config_name!r}")
        return await self._patch(
            f"/v1/customization/configs/{namespace}/{config_name}",
            body=await async_maybe_transform(
                {
                    "add_training_options": add_training_options,
                    "chat_prompt_template": chat_prompt_template,
                    "custom_fields": custom_fields,
                    "dataset_schemas": dataset_schemas,
                    "description": description,
                    "max_seq_length": max_seq_length,
                    "ownership": ownership,
                    "pod_spec": pod_spec,
                    "project": project,
                    "prompt_template": prompt_template,
                    "remove_training_options": remove_training_options,
                    "training_options": training_options,
                    "training_precision": training_precision,
                },
                config_update_params.ConfigUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CustomizationConfig,
        )

    def list(
        self,
        *,
        filter: CustomizationConfigFilterParam | NotGiven = NOT_GIVEN,
        page: int | NotGiven = NOT_GIVEN,
        page_size: int | NotGiven = NOT_GIVEN,
        sort: CustomizationConfigSortField | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AsyncPaginator[CustomizationConfig, AsyncDefaultPagination[CustomizationConfig]]:
        """
        List available customization configs.

        Args:
          filter: Filter customization configs on various criteria.

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
            "/v1/customization/configs",
            page=AsyncDefaultPagination[CustomizationConfig],
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
                    config_list_params.ConfigListParams,
                ),
            ),
            model=CustomizationConfig,
        )

    async def delete(
        self,
        config_name: str,
        *,
        namespace: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """
        Delete Customization Config

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not namespace:
            raise ValueError(f"Expected a non-empty value for `namespace` but received {namespace!r}")
        if not config_name:
            raise ValueError(f"Expected a non-empty value for `config_name` but received {config_name!r}")
        return await self._delete(
            f"/v1/customization/configs/{namespace}/{config_name}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )


class ConfigsResourceWithRawResponse:
    def __init__(self, configs: ConfigsResource) -> None:
        self._configs = configs

        self.create = to_raw_response_wrapper(
            configs.create,
        )
        self.retrieve = to_raw_response_wrapper(
            configs.retrieve,
        )
        self.update = to_raw_response_wrapper(
            configs.update,
        )
        self.list = to_raw_response_wrapper(
            configs.list,
        )
        self.delete = to_raw_response_wrapper(
            configs.delete,
        )


class AsyncConfigsResourceWithRawResponse:
    def __init__(self, configs: AsyncConfigsResource) -> None:
        self._configs = configs

        self.create = async_to_raw_response_wrapper(
            configs.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            configs.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            configs.update,
        )
        self.list = async_to_raw_response_wrapper(
            configs.list,
        )
        self.delete = async_to_raw_response_wrapper(
            configs.delete,
        )


class ConfigsResourceWithStreamingResponse:
    def __init__(self, configs: ConfigsResource) -> None:
        self._configs = configs

        self.create = to_streamed_response_wrapper(
            configs.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            configs.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            configs.update,
        )
        self.list = to_streamed_response_wrapper(
            configs.list,
        )
        self.delete = to_streamed_response_wrapper(
            configs.delete,
        )


class AsyncConfigsResourceWithStreamingResponse:
    def __init__(self, configs: AsyncConfigsResource) -> None:
        self._configs = configs

        self.create = async_to_streamed_response_wrapper(
            configs.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            configs.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            configs.update,
        )
        self.list = async_to_streamed_response_wrapper(
            configs.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            configs.delete,
        )
