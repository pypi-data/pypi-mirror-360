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

from typing import Dict

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
from ...types.evaluation import result_list_params, result_create_params, result_update_params
from ...types.evaluation_result import EvaluationResult
from ...types.shared.delete_response import DeleteResponse
from ...types.shared_params.ownership import Ownership
from ...types.shared.generic_sort_field import GenericSortField
from ...types.evaluation.task_result_param import TaskResultParam
from ...types.evaluation.group_result_param import GroupResultParam
from ...types.evaluation.evaluation_result_filter_param import EvaluationResultFilterParam

__all__ = ["ResultsResource", "AsyncResultsResource"]


class ResultsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ResultsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#accessing-raw-response-data-e-g-headers
        """
        return ResultsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ResultsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#with_streaming_response
        """
        return ResultsResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        job: str,
        custom_fields: Dict[str, str] | NotGiven = NOT_GIVEN,
        description: str | NotGiven = NOT_GIVEN,
        files_url: str | NotGiven = NOT_GIVEN,
        groups: Dict[str, GroupResultParam] | NotGiven = NOT_GIVEN,
        namespace: str | NotGiven = NOT_GIVEN,
        ownership: Ownership | NotGiven = NOT_GIVEN,
        project: str | NotGiven = NOT_GIVEN,
        tasks: Dict[str, TaskResultParam] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> EvaluationResult:
        """
        Create a new evaluation result.

        Args:
          job: The evaluation job associated with this results instance.

          custom_fields: A set of custom fields that the user can define and use for various purposes.

          description: The description of the entity.

          files_url: The place for the output files, if any.

          groups: The results at the group-level.

          namespace: The namespace of the entity. This can be missing for namespace entities or in
              deployments that don't use namespaces.

          ownership: Information about ownership of an entity.

              If the entity is a namespace, the `access_policies` will typically apply to all
              entities inside the namespace.

          project: The URN of the project associated with this entity.

          tasks: The results at the task-level.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/v1/evaluation/results",
            body=maybe_transform(
                {
                    "job": job,
                    "custom_fields": custom_fields,
                    "description": description,
                    "files_url": files_url,
                    "groups": groups,
                    "namespace": namespace,
                    "ownership": ownership,
                    "project": project,
                    "tasks": tasks,
                },
                result_create_params.ResultCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=EvaluationResult,
        )

    def retrieve(
        self,
        result_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> EvaluationResult:
        """
        Get evaluation result info.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not result_id:
            raise ValueError(f"Expected a non-empty value for `result_id` but received {result_id!r}")
        return self._get(
            f"/v1/evaluation/results/{result_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=EvaluationResult,
        )

    def update(
        self,
        result_id: str,
        *,
        custom_fields: Dict[str, str] | NotGiven = NOT_GIVEN,
        description: str | NotGiven = NOT_GIVEN,
        files_url: str | NotGiven = NOT_GIVEN,
        groups: Dict[str, GroupResultParam] | NotGiven = NOT_GIVEN,
        job: str | NotGiven = NOT_GIVEN,
        namespace: str | NotGiven = NOT_GIVEN,
        ownership: Ownership | NotGiven = NOT_GIVEN,
        project: str | NotGiven = NOT_GIVEN,
        tasks: Dict[str, TaskResultParam] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> EvaluationResult:
        """
        Update the evaluation result.

        Args:
          custom_fields: A set of custom fields that the user can define and use for various purposes.

          description: The description of the entity.

          files_url: The place for the output files, if any.

          groups: The results at the group-level.

          job: The evaluation job associated with this results instance.

          namespace: The namespace of the entity. This can be missing for namespace entities or in
              deployments that don't use namespaces.

          ownership: Information about ownership of an entity.

              If the entity is a namespace, the `access_policies` will typically apply to all
              entities inside the namespace.

          project: The URN of the project associated with this entity.

          tasks: The results at the task-level.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not result_id:
            raise ValueError(f"Expected a non-empty value for `result_id` but received {result_id!r}")
        return self._patch(
            f"/v1/evaluation/results/{result_id}",
            body=maybe_transform(
                {
                    "custom_fields": custom_fields,
                    "description": description,
                    "files_url": files_url,
                    "groups": groups,
                    "job": job,
                    "namespace": namespace,
                    "ownership": ownership,
                    "project": project,
                    "tasks": tasks,
                },
                result_update_params.ResultUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=EvaluationResult,
        )

    def list(
        self,
        *,
        filter: EvaluationResultFilterParam | NotGiven = NOT_GIVEN,
        page: int | NotGiven = NOT_GIVEN,
        page_size: int | NotGiven = NOT_GIVEN,
        sort: GenericSortField | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SyncDefaultPagination[EvaluationResult]:
        """
        List available evaluation results.

        Args:
          filter: Filter results on various criteria.

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
            "/v1/evaluation/results",
            page=SyncDefaultPagination[EvaluationResult],
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
                    result_list_params.ResultListParams,
                ),
            ),
            model=EvaluationResult,
        )

    def delete(
        self,
        result_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DeleteResponse:
        """
        Delete Evaluation Result

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not result_id:
            raise ValueError(f"Expected a non-empty value for `result_id` but received {result_id!r}")
        return self._delete(
            f"/v1/evaluation/results/{result_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DeleteResponse,
        )


class AsyncResultsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncResultsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#accessing-raw-response-data-e-g-headers
        """
        return AsyncResultsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncResultsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://docs.nvidia.com/nemo/microservices/latest/pysdk/index.html#with_streaming_response
        """
        return AsyncResultsResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        job: str,
        custom_fields: Dict[str, str] | NotGiven = NOT_GIVEN,
        description: str | NotGiven = NOT_GIVEN,
        files_url: str | NotGiven = NOT_GIVEN,
        groups: Dict[str, GroupResultParam] | NotGiven = NOT_GIVEN,
        namespace: str | NotGiven = NOT_GIVEN,
        ownership: Ownership | NotGiven = NOT_GIVEN,
        project: str | NotGiven = NOT_GIVEN,
        tasks: Dict[str, TaskResultParam] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> EvaluationResult:
        """
        Create a new evaluation result.

        Args:
          job: The evaluation job associated with this results instance.

          custom_fields: A set of custom fields that the user can define and use for various purposes.

          description: The description of the entity.

          files_url: The place for the output files, if any.

          groups: The results at the group-level.

          namespace: The namespace of the entity. This can be missing for namespace entities or in
              deployments that don't use namespaces.

          ownership: Information about ownership of an entity.

              If the entity is a namespace, the `access_policies` will typically apply to all
              entities inside the namespace.

          project: The URN of the project associated with this entity.

          tasks: The results at the task-level.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/v1/evaluation/results",
            body=await async_maybe_transform(
                {
                    "job": job,
                    "custom_fields": custom_fields,
                    "description": description,
                    "files_url": files_url,
                    "groups": groups,
                    "namespace": namespace,
                    "ownership": ownership,
                    "project": project,
                    "tasks": tasks,
                },
                result_create_params.ResultCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=EvaluationResult,
        )

    async def retrieve(
        self,
        result_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> EvaluationResult:
        """
        Get evaluation result info.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not result_id:
            raise ValueError(f"Expected a non-empty value for `result_id` but received {result_id!r}")
        return await self._get(
            f"/v1/evaluation/results/{result_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=EvaluationResult,
        )

    async def update(
        self,
        result_id: str,
        *,
        custom_fields: Dict[str, str] | NotGiven = NOT_GIVEN,
        description: str | NotGiven = NOT_GIVEN,
        files_url: str | NotGiven = NOT_GIVEN,
        groups: Dict[str, GroupResultParam] | NotGiven = NOT_GIVEN,
        job: str | NotGiven = NOT_GIVEN,
        namespace: str | NotGiven = NOT_GIVEN,
        ownership: Ownership | NotGiven = NOT_GIVEN,
        project: str | NotGiven = NOT_GIVEN,
        tasks: Dict[str, TaskResultParam] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> EvaluationResult:
        """
        Update the evaluation result.

        Args:
          custom_fields: A set of custom fields that the user can define and use for various purposes.

          description: The description of the entity.

          files_url: The place for the output files, if any.

          groups: The results at the group-level.

          job: The evaluation job associated with this results instance.

          namespace: The namespace of the entity. This can be missing for namespace entities or in
              deployments that don't use namespaces.

          ownership: Information about ownership of an entity.

              If the entity is a namespace, the `access_policies` will typically apply to all
              entities inside the namespace.

          project: The URN of the project associated with this entity.

          tasks: The results at the task-level.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not result_id:
            raise ValueError(f"Expected a non-empty value for `result_id` but received {result_id!r}")
        return await self._patch(
            f"/v1/evaluation/results/{result_id}",
            body=await async_maybe_transform(
                {
                    "custom_fields": custom_fields,
                    "description": description,
                    "files_url": files_url,
                    "groups": groups,
                    "job": job,
                    "namespace": namespace,
                    "ownership": ownership,
                    "project": project,
                    "tasks": tasks,
                },
                result_update_params.ResultUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=EvaluationResult,
        )

    def list(
        self,
        *,
        filter: EvaluationResultFilterParam | NotGiven = NOT_GIVEN,
        page: int | NotGiven = NOT_GIVEN,
        page_size: int | NotGiven = NOT_GIVEN,
        sort: GenericSortField | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AsyncPaginator[EvaluationResult, AsyncDefaultPagination[EvaluationResult]]:
        """
        List available evaluation results.

        Args:
          filter: Filter results on various criteria.

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
            "/v1/evaluation/results",
            page=AsyncDefaultPagination[EvaluationResult],
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
                    result_list_params.ResultListParams,
                ),
            ),
            model=EvaluationResult,
        )

    async def delete(
        self,
        result_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DeleteResponse:
        """
        Delete Evaluation Result

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not result_id:
            raise ValueError(f"Expected a non-empty value for `result_id` but received {result_id!r}")
        return await self._delete(
            f"/v1/evaluation/results/{result_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DeleteResponse,
        )


class ResultsResourceWithRawResponse:
    def __init__(self, results: ResultsResource) -> None:
        self._results = results

        self.create = to_raw_response_wrapper(
            results.create,
        )
        self.retrieve = to_raw_response_wrapper(
            results.retrieve,
        )
        self.update = to_raw_response_wrapper(
            results.update,
        )
        self.list = to_raw_response_wrapper(
            results.list,
        )
        self.delete = to_raw_response_wrapper(
            results.delete,
        )


class AsyncResultsResourceWithRawResponse:
    def __init__(self, results: AsyncResultsResource) -> None:
        self._results = results

        self.create = async_to_raw_response_wrapper(
            results.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            results.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            results.update,
        )
        self.list = async_to_raw_response_wrapper(
            results.list,
        )
        self.delete = async_to_raw_response_wrapper(
            results.delete,
        )


class ResultsResourceWithStreamingResponse:
    def __init__(self, results: ResultsResource) -> None:
        self._results = results

        self.create = to_streamed_response_wrapper(
            results.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            results.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            results.update,
        )
        self.list = to_streamed_response_wrapper(
            results.list,
        )
        self.delete = to_streamed_response_wrapper(
            results.delete,
        )


class AsyncResultsResourceWithStreamingResponse:
    def __init__(self, results: AsyncResultsResource) -> None:
        self._results = results

        self.create = async_to_streamed_response_wrapper(
            results.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            results.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            results.update,
        )
        self.list = async_to_streamed_response_wrapper(
            results.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            results.delete,
        )
