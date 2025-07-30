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

from typing import Dict, Union

import httpx

from ..types import ModelSortField, model_list_params, model_create_params, model_update_params
from .._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from .._utils import maybe_transform, async_maybe_transform
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ..pagination import SyncDefaultPagination, AsyncDefaultPagination
from ..types.model import Model
from .._base_client import AsyncPaginator, make_request_options
from ..types.model_sort_field import ModelSortField
from ..types.model_filter_param import ModelFilterParam
from ..types.shared.delete_response import DeleteResponse
from ..types.shared_params.ownership import Ownership
from ..types.shared_params.model_spec import ModelSpec
from ..types.shared_params.prompt_data import PromptData
from ..types.shared_params.model_artifact import ModelArtifact
from ..types.shared_params.api_endpoint_data import APIEndpointData
from ..types.shared_params.guardrail_config_param import GuardrailConfigParam
from ..types.shared_params.parameter_efficient_finetuning_data import ParameterEfficientFinetuningData

__all__ = ["ModelsResource", "AsyncModelsResource"]


class ModelsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ModelsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#accessing-raw-response-data-e-g-headers
        """
        return ModelsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ModelsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#with_streaming_response
        """
        return ModelsResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        api_endpoint: APIEndpointData | NotGiven = NOT_GIVEN,
        artifact: ModelArtifact | NotGiven = NOT_GIVEN,
        base_model: Union[str, object] | NotGiven = NOT_GIVEN,
        custom_fields: Dict[str, str] | NotGiven = NOT_GIVEN,
        description: str | NotGiven = NOT_GIVEN,
        guardrails: GuardrailConfigParam | NotGiven = NOT_GIVEN,
        name: str | NotGiven = NOT_GIVEN,
        namespace: str | NotGiven = NOT_GIVEN,
        ownership: Ownership | NotGiven = NOT_GIVEN,
        peft: ParameterEfficientFinetuningData | NotGiven = NOT_GIVEN,
        project: str | NotGiven = NOT_GIVEN,
        prompt: PromptData | NotGiven = NOT_GIVEN,
        spec: ModelSpec | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Model:
        """
        Create a new model.

        Args:
          api_endpoint: Data about an API endpoint.

          artifact: Data about a model artifact (a set of checkpoint files, configs, and other
              auxiliary info).

              The `files_url` field can point to a DataStore location.

              Example:

              - nds://models/rdinu/my-lora-customization

              The `rdinu/my-lora-customization` part above is the actual repository.

              If a specific revision needs to be referred, the HuggingFace syntax is used.

              - nds://models/rdinu/my-lora-customization@v1
              - nds://models/rdinu/my-lora-customization@8df79a8

          base_model: Link to another model which is used as a base for the current model.

          custom_fields: A set of custom fields that the user can define and use for various purposes.

          description: The description of the entity.

          guardrails: A guardrail configuration

          name: The name of the entity. Must be unique inside the namespace. If not specified,
              it will be the same as the automatically generated id.

          namespace: The namespace of the entity. This can be missing for namespace entities or in
              deployments that don't use namespaces.

          ownership: Information about ownership of an entity.

              If the entity is a namespace, the `access_policies` will typically apply to all
              entities inside the namespace.

          peft: Data about a parameter-efficient finetuning.

          project: The URN of the project associated with this entity.

          prompt: Prompt engineering data.

          spec: Detailed specification about a model.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/v1/models",
            body=maybe_transform(
                {
                    "api_endpoint": api_endpoint,
                    "artifact": artifact,
                    "base_model": base_model,
                    "custom_fields": custom_fields,
                    "description": description,
                    "guardrails": guardrails,
                    "name": name,
                    "namespace": namespace,
                    "ownership": ownership,
                    "peft": peft,
                    "project": project,
                    "prompt": prompt,
                    "spec": spec,
                },
                model_create_params.ModelCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Model,
        )

    def retrieve(
        self,
        model_name: str,
        *,
        namespace: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Model:
        """
        Get model info.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not namespace:
            raise ValueError(f"Expected a non-empty value for `namespace` but received {namespace!r}")
        if not model_name:
            raise ValueError(f"Expected a non-empty value for `model_name` but received {model_name!r}")
        return self._get(
            f"/v1/models/{namespace}/{model_name}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Model,
        )

    def update(
        self,
        model_name: str,
        *,
        namespace: str,
        api_endpoint: APIEndpointData | NotGiven = NOT_GIVEN,
        artifact: ModelArtifact | NotGiven = NOT_GIVEN,
        base_model: model_update_params.BaseModel | NotGiven = NOT_GIVEN,
        custom_fields: Dict[str, str] | NotGiven = NOT_GIVEN,
        description: str | NotGiven = NOT_GIVEN,
        guardrails: GuardrailConfigParam | NotGiven = NOT_GIVEN,
        ownership: Ownership | NotGiven = NOT_GIVEN,
        peft: ParameterEfficientFinetuningData | NotGiven = NOT_GIVEN,
        project: str | NotGiven = NOT_GIVEN,
        prompt: PromptData | NotGiven = NOT_GIVEN,
        schema_version: str | NotGiven = NOT_GIVEN,
        spec: ModelSpec | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Model:
        """Update model metadata.

        If the request body has an empty field, keep the old
        value.

        Args:
          api_endpoint: Data about an API endpoint.

          artifact: Data about a model artifact (a set of checkpoint files, configs, and other
              auxiliary info).

              The `files_url` field can point to a DataStore location.

              Example:

              - nds://models/rdinu/my-lora-customization

              The `rdinu/my-lora-customization` part above is the actual repository.

              If a specific revision needs to be referred, the HuggingFace syntax is used.

              - nds://models/rdinu/my-lora-customization@v1
              - nds://models/rdinu/my-lora-customization@8df79a8

          base_model: Link to another model which is used as a base for the current model.

          custom_fields: A set of custom fields that the user can define and use for various purposes.

          description: The description of the entity.

          guardrails: A guardrail configuration

          ownership: Information about ownership of an entity.

              If the entity is a namespace, the `access_policies` will typically apply to all
              entities inside the namespace.

          peft: Data about a parameter-efficient finetuning.

          project: The URN of the project associated with this entity.

          prompt: Prompt engineering data.

          schema_version: The version of the schema for the object. Internal use only.

          spec: Detailed specification about a model.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not namespace:
            raise ValueError(f"Expected a non-empty value for `namespace` but received {namespace!r}")
        if not model_name:
            raise ValueError(f"Expected a non-empty value for `model_name` but received {model_name!r}")
        return self._patch(
            f"/v1/models/{namespace}/{model_name}",
            body=maybe_transform(
                {
                    "api_endpoint": api_endpoint,
                    "artifact": artifact,
                    "base_model": base_model,
                    "custom_fields": custom_fields,
                    "description": description,
                    "guardrails": guardrails,
                    "ownership": ownership,
                    "peft": peft,
                    "project": project,
                    "prompt": prompt,
                    "schema_version": schema_version,
                    "spec": spec,
                },
                model_update_params.ModelUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Model,
        )

    def list(
        self,
        *,
        filter: ModelFilterParam | NotGiven = NOT_GIVEN,
        page: int | NotGiven = NOT_GIVEN,
        page_size: int | NotGiven = NOT_GIVEN,
        sort: ModelSortField | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SyncDefaultPagination[Model]:
        """
        Return the list of available models.

        Args:
          filter: Filter models on various criteria.

              Where it makes sense, you can also filter on the existence of a property. For
              example:

              - `?filter[peft]=true`: would filter all models with `peft` attribute set.

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
            "/v1/models",
            page=SyncDefaultPagination[Model],
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
                    model_list_params.ModelListParams,
                ),
            ),
            model=Model,
        )

    def delete(
        self,
        model_name: str,
        *,
        namespace: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DeleteResponse:
        """
        Delete Model

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not namespace:
            raise ValueError(f"Expected a non-empty value for `namespace` but received {namespace!r}")
        if not model_name:
            raise ValueError(f"Expected a non-empty value for `model_name` but received {model_name!r}")
        return self._delete(
            f"/v1/models/{namespace}/{model_name}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DeleteResponse,
        )


class AsyncModelsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncModelsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#accessing-raw-response-data-e-g-headers
        """
        return AsyncModelsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncModelsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#with_streaming_response
        """
        return AsyncModelsResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        api_endpoint: APIEndpointData | NotGiven = NOT_GIVEN,
        artifact: ModelArtifact | NotGiven = NOT_GIVEN,
        base_model: Union[str, object] | NotGiven = NOT_GIVEN,
        custom_fields: Dict[str, str] | NotGiven = NOT_GIVEN,
        description: str | NotGiven = NOT_GIVEN,
        guardrails: GuardrailConfigParam | NotGiven = NOT_GIVEN,
        name: str | NotGiven = NOT_GIVEN,
        namespace: str | NotGiven = NOT_GIVEN,
        ownership: Ownership | NotGiven = NOT_GIVEN,
        peft: ParameterEfficientFinetuningData | NotGiven = NOT_GIVEN,
        project: str | NotGiven = NOT_GIVEN,
        prompt: PromptData | NotGiven = NOT_GIVEN,
        spec: ModelSpec | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Model:
        """
        Create a new model.

        Args:
          api_endpoint: Data about an API endpoint.

          artifact: Data about a model artifact (a set of checkpoint files, configs, and other
              auxiliary info).

              The `files_url` field can point to a DataStore location.

              Example:

              - nds://models/rdinu/my-lora-customization

              The `rdinu/my-lora-customization` part above is the actual repository.

              If a specific revision needs to be referred, the HuggingFace syntax is used.

              - nds://models/rdinu/my-lora-customization@v1
              - nds://models/rdinu/my-lora-customization@8df79a8

          base_model: Link to another model which is used as a base for the current model.

          custom_fields: A set of custom fields that the user can define and use for various purposes.

          description: The description of the entity.

          guardrails: A guardrail configuration

          name: The name of the entity. Must be unique inside the namespace. If not specified,
              it will be the same as the automatically generated id.

          namespace: The namespace of the entity. This can be missing for namespace entities or in
              deployments that don't use namespaces.

          ownership: Information about ownership of an entity.

              If the entity is a namespace, the `access_policies` will typically apply to all
              entities inside the namespace.

          peft: Data about a parameter-efficient finetuning.

          project: The URN of the project associated with this entity.

          prompt: Prompt engineering data.

          spec: Detailed specification about a model.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/v1/models",
            body=await async_maybe_transform(
                {
                    "api_endpoint": api_endpoint,
                    "artifact": artifact,
                    "base_model": base_model,
                    "custom_fields": custom_fields,
                    "description": description,
                    "guardrails": guardrails,
                    "name": name,
                    "namespace": namespace,
                    "ownership": ownership,
                    "peft": peft,
                    "project": project,
                    "prompt": prompt,
                    "spec": spec,
                },
                model_create_params.ModelCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Model,
        )

    async def retrieve(
        self,
        model_name: str,
        *,
        namespace: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Model:
        """
        Get model info.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not namespace:
            raise ValueError(f"Expected a non-empty value for `namespace` but received {namespace!r}")
        if not model_name:
            raise ValueError(f"Expected a non-empty value for `model_name` but received {model_name!r}")
        return await self._get(
            f"/v1/models/{namespace}/{model_name}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Model,
        )

    async def update(
        self,
        model_name: str,
        *,
        namespace: str,
        api_endpoint: APIEndpointData | NotGiven = NOT_GIVEN,
        artifact: ModelArtifact | NotGiven = NOT_GIVEN,
        base_model: model_update_params.BaseModel | NotGiven = NOT_GIVEN,
        custom_fields: Dict[str, str] | NotGiven = NOT_GIVEN,
        description: str | NotGiven = NOT_GIVEN,
        guardrails: GuardrailConfigParam | NotGiven = NOT_GIVEN,
        ownership: Ownership | NotGiven = NOT_GIVEN,
        peft: ParameterEfficientFinetuningData | NotGiven = NOT_GIVEN,
        project: str | NotGiven = NOT_GIVEN,
        prompt: PromptData | NotGiven = NOT_GIVEN,
        schema_version: str | NotGiven = NOT_GIVEN,
        spec: ModelSpec | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Model:
        """Update model metadata.

        If the request body has an empty field, keep the old
        value.

        Args:
          api_endpoint: Data about an API endpoint.

          artifact: Data about a model artifact (a set of checkpoint files, configs, and other
              auxiliary info).

              The `files_url` field can point to a DataStore location.

              Example:

              - nds://models/rdinu/my-lora-customization

              The `rdinu/my-lora-customization` part above is the actual repository.

              If a specific revision needs to be referred, the HuggingFace syntax is used.

              - nds://models/rdinu/my-lora-customization@v1
              - nds://models/rdinu/my-lora-customization@8df79a8

          base_model: Link to another model which is used as a base for the current model.

          custom_fields: A set of custom fields that the user can define and use for various purposes.

          description: The description of the entity.

          guardrails: A guardrail configuration

          ownership: Information about ownership of an entity.

              If the entity is a namespace, the `access_policies` will typically apply to all
              entities inside the namespace.

          peft: Data about a parameter-efficient finetuning.

          project: The URN of the project associated with this entity.

          prompt: Prompt engineering data.

          schema_version: The version of the schema for the object. Internal use only.

          spec: Detailed specification about a model.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not namespace:
            raise ValueError(f"Expected a non-empty value for `namespace` but received {namespace!r}")
        if not model_name:
            raise ValueError(f"Expected a non-empty value for `model_name` but received {model_name!r}")
        return await self._patch(
            f"/v1/models/{namespace}/{model_name}",
            body=await async_maybe_transform(
                {
                    "api_endpoint": api_endpoint,
                    "artifact": artifact,
                    "base_model": base_model,
                    "custom_fields": custom_fields,
                    "description": description,
                    "guardrails": guardrails,
                    "ownership": ownership,
                    "peft": peft,
                    "project": project,
                    "prompt": prompt,
                    "schema_version": schema_version,
                    "spec": spec,
                },
                model_update_params.ModelUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Model,
        )

    def list(
        self,
        *,
        filter: ModelFilterParam | NotGiven = NOT_GIVEN,
        page: int | NotGiven = NOT_GIVEN,
        page_size: int | NotGiven = NOT_GIVEN,
        sort: ModelSortField | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AsyncPaginator[Model, AsyncDefaultPagination[Model]]:
        """
        Return the list of available models.

        Args:
          filter: Filter models on various criteria.

              Where it makes sense, you can also filter on the existence of a property. For
              example:

              - `?filter[peft]=true`: would filter all models with `peft` attribute set.

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
            "/v1/models",
            page=AsyncDefaultPagination[Model],
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
                    model_list_params.ModelListParams,
                ),
            ),
            model=Model,
        )

    async def delete(
        self,
        model_name: str,
        *,
        namespace: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DeleteResponse:
        """
        Delete Model

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not namespace:
            raise ValueError(f"Expected a non-empty value for `namespace` but received {namespace!r}")
        if not model_name:
            raise ValueError(f"Expected a non-empty value for `model_name` but received {model_name!r}")
        return await self._delete(
            f"/v1/models/{namespace}/{model_name}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DeleteResponse,
        )


class ModelsResourceWithRawResponse:
    def __init__(self, models: ModelsResource) -> None:
        self._models = models

        self.create = to_raw_response_wrapper(
            models.create,
        )
        self.retrieve = to_raw_response_wrapper(
            models.retrieve,
        )
        self.update = to_raw_response_wrapper(
            models.update,
        )
        self.list = to_raw_response_wrapper(
            models.list,
        )
        self.delete = to_raw_response_wrapper(
            models.delete,
        )


class AsyncModelsResourceWithRawResponse:
    def __init__(self, models: AsyncModelsResource) -> None:
        self._models = models

        self.create = async_to_raw_response_wrapper(
            models.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            models.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            models.update,
        )
        self.list = async_to_raw_response_wrapper(
            models.list,
        )
        self.delete = async_to_raw_response_wrapper(
            models.delete,
        )


class ModelsResourceWithStreamingResponse:
    def __init__(self, models: ModelsResource) -> None:
        self._models = models

        self.create = to_streamed_response_wrapper(
            models.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            models.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            models.update,
        )
        self.list = to_streamed_response_wrapper(
            models.list,
        )
        self.delete = to_streamed_response_wrapper(
            models.delete,
        )


class AsyncModelsResourceWithStreamingResponse:
    def __init__(self, models: AsyncModelsResource) -> None:
        self._models = models

        self.create = async_to_streamed_response_wrapper(
            models.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            models.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            models.update,
        )
        self.list = async_to_streamed_response_wrapper(
            models.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            models.delete,
        )
