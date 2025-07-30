# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable

import httpx

from ..._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ..._utils import maybe_transform, strip_not_given, async_maybe_transform
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
    job_list_params,
    job_create_params,
)
from ...types.customization.job_logs import JobLogs
from ...types.shared_params.ownership import Ownership
from ...types.shared.generic_sort_field import GenericSortField
from ...types.customization.hyperparameters_param import HyperparametersParam
from ...types.customization.customization_job_output import CustomizationJobOutput
from ...types.customization.wand_b_integration_param import WandBIntegrationParam
from ...types.customization.customization_status_details import CustomizationStatusDetails
from ...types.customization.dataset_parameters_input_param import DatasetParametersInputParam
from ...types.customization.customization_job_list_filter_param import CustomizationJobListFilterParam

__all__ = ["JobsResource", "AsyncJobsResource"]


class JobsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> JobsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/stainless-sdks/nemo-microservices-v1-python#accessing-raw-response-data-eg-headers
        """
        return JobsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> JobsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/stainless-sdks/nemo-microservices-v1-python#with_streaming_response
        """
        return JobsResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        config: job_create_params.Config,
        dataset: job_create_params.Dataset,
        hyperparameters: HyperparametersParam,
        dataset_parameters: DatasetParametersInputParam | NotGiven = NOT_GIVEN,
        description: str | NotGiven = NOT_GIVEN,
        integrations: Iterable[WandBIntegrationParam] | NotGiven = NOT_GIVEN,
        name: str | NotGiven = NOT_GIVEN,
        output_model: str | NotGiven = NOT_GIVEN,
        ownership: Ownership | NotGiven = NOT_GIVEN,
        project: str | NotGiven = NOT_GIVEN,
        wandb_api_key: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CustomizationJobOutput:
        """
        Create a new customization job.

        ## W&B Integration

        Available W&B settings are mapped to the W&B python sdk settings:
        https://docs.wandb.ai/ref/python/init

        To enable W&B (Weights & Biases) integration, include your W&B API key in the
        request header:

        ```
        wandb-api-key: <YOUR_W&B_API_KEY>
        ```

        **Note**: W&B integration is optional. Jobs can be created without W&B by
        omitting the API key header.

        ### W&B Configuration Priority

        W&B settings are applied with the following priority (highest priority overrides
        lower):

        1. **Lowest Priority - Job Fields**:

           - `job.project` → sets W&B project name
           - `job.description` → sets W&B notes

        2. **Medium Priority - Application Deployment Settings**:

           - Deployment-specific settings from Helm chart values.yaml under `wandb`
             section

        3. **Highest Priority - Job Integrations**:
           - Settings from `job.integrations` array with `type: "wandb"`
           - These settings will override all other W&B configurations

        ### Example of W&B Integration in Request Body

        ```json
        {
          "integrations": [
            {
              "type": "wandb",
              "wandb": {
                "project": "custom-wandb-project",
                "entity": "custom-team-or-username",
                "notes": "Custom notes about this run",
                "tags": ["fine-tuning", "llama"]
              }
            }
          ]
          // ... other job request body fields
        }
        ```

        Args:
          config: The customization configuration to be used.

          dataset: The dataset to be used for customization.

          hyperparameters: The hyperparameters to be used for customization.

          dataset_parameters: Additional parameters to configure a dataset

          description: The description of the entity.

          integrations: A list of third party integrations for a job. Example: Weights & Biases
              integration.

          name: The name of the entity. Must be unique inside the namespace. If not specified,
              it will be the same as the automatically generated id.

          output_model: The output model. If not specified, no output model is created, only the
              artifact files written.

          ownership: Information about ownership of an entity.

              If the entity is a namespace, the `access_policies` will typically apply to all
              entities inside the namespace.

          project: The URN of the project associated with this entity.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {**strip_not_given({"wandb-api-key": wandb_api_key}), **(extra_headers or {})}
        return self._post(
            "/v1/customization/jobs",
            body=maybe_transform(
                {
                    "config": config,
                    "dataset": dataset,
                    "hyperparameters": hyperparameters,
                    "dataset_parameters": dataset_parameters,
                    "description": description,
                    "integrations": integrations,
                    "name": name,
                    "output_model": output_model,
                    "ownership": ownership,
                    "project": project,
                },
                job_create_params.JobCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CustomizationJobOutput,
        )

    def retrieve(
        self,
        job_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CustomizationJobOutput:
        """
        Get info about a customization job.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not job_id:
            raise ValueError(f"Expected a non-empty value for `job_id` but received {job_id!r}")
        return self._get(
            f"/v1/customization/jobs/{job_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CustomizationJobOutput,
        )

    def list(
        self,
        *,
        filter: CustomizationJobListFilterParam | NotGiven = NOT_GIVEN,
        page: int | NotGiven = NOT_GIVEN,
        page_size: int | NotGiven = NOT_GIVEN,
        sort: GenericSortField | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SyncDefaultPagination[CustomizationJobOutput]:
        """
        List available customization jobs.

        Args:
          filter: Filter jobs on various criteria.

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
            "/v1/customization/jobs",
            page=SyncDefaultPagination[CustomizationJobOutput],
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
                    job_list_params.JobListParams,
                ),
            ),
            model=CustomizationJobOutput,
        )

    def cancel(
        self,
        job_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CustomizationJobOutput:
        """
        Cancel a customization job.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not job_id:
            raise ValueError(f"Expected a non-empty value for `job_id` but received {job_id!r}")
        return self._post(
            f"/v1/customization/jobs/{job_id}/cancel",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CustomizationJobOutput,
        )

    def container_logs(
        self,
        job_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> JobLogs:
        """
        List the metrics emitted from training.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not job_id:
            raise ValueError(f"Expected a non-empty value for `job_id` but received {job_id!r}")
        return self._get(
            f"/v1/customization/jobs/{job_id}/container-logs",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=JobLogs,
        )

    def status(
        self,
        job_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CustomizationStatusDetails:
        """
        List the metrics emitted from training.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not job_id:
            raise ValueError(f"Expected a non-empty value for `job_id` but received {job_id!r}")
        return self._get(
            f"/v1/customization/jobs/{job_id}/status",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CustomizationStatusDetails,
        )


class AsyncJobsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncJobsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/stainless-sdks/nemo-microservices-v1-python#accessing-raw-response-data-eg-headers
        """
        return AsyncJobsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncJobsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/stainless-sdks/nemo-microservices-v1-python#with_streaming_response
        """
        return AsyncJobsResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        config: job_create_params.Config,
        dataset: job_create_params.Dataset,
        hyperparameters: HyperparametersParam,
        dataset_parameters: DatasetParametersInputParam | NotGiven = NOT_GIVEN,
        description: str | NotGiven = NOT_GIVEN,
        integrations: Iterable[WandBIntegrationParam] | NotGiven = NOT_GIVEN,
        name: str | NotGiven = NOT_GIVEN,
        output_model: str | NotGiven = NOT_GIVEN,
        ownership: Ownership | NotGiven = NOT_GIVEN,
        project: str | NotGiven = NOT_GIVEN,
        wandb_api_key: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CustomizationJobOutput:
        """
        Create a new customization job.

        ## W&B Integration

        Available W&B settings are mapped to the W&B python sdk settings:
        https://docs.wandb.ai/ref/python/init

        To enable W&B (Weights & Biases) integration, include your W&B API key in the
        request header:

        ```
        wandb-api-key: <YOUR_W&B_API_KEY>
        ```

        **Note**: W&B integration is optional. Jobs can be created without W&B by
        omitting the API key header.

        ### W&B Configuration Priority

        W&B settings are applied with the following priority (highest priority overrides
        lower):

        1. **Lowest Priority - Job Fields**:

           - `job.project` → sets W&B project name
           - `job.description` → sets W&B notes

        2. **Medium Priority - Application Deployment Settings**:

           - Deployment-specific settings from Helm chart values.yaml under `wandb`
             section

        3. **Highest Priority - Job Integrations**:
           - Settings from `job.integrations` array with `type: "wandb"`
           - These settings will override all other W&B configurations

        ### Example of W&B Integration in Request Body

        ```json
        {
          "integrations": [
            {
              "type": "wandb",
              "wandb": {
                "project": "custom-wandb-project",
                "entity": "custom-team-or-username",
                "notes": "Custom notes about this run",
                "tags": ["fine-tuning", "llama"]
              }
            }
          ]
          // ... other job request body fields
        }
        ```

        Args:
          config: The customization configuration to be used.

          dataset: The dataset to be used for customization.

          hyperparameters: The hyperparameters to be used for customization.

          dataset_parameters: Additional parameters to configure a dataset

          description: The description of the entity.

          integrations: A list of third party integrations for a job. Example: Weights & Biases
              integration.

          name: The name of the entity. Must be unique inside the namespace. If not specified,
              it will be the same as the automatically generated id.

          output_model: The output model. If not specified, no output model is created, only the
              artifact files written.

          ownership: Information about ownership of an entity.

              If the entity is a namespace, the `access_policies` will typically apply to all
              entities inside the namespace.

          project: The URN of the project associated with this entity.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {**strip_not_given({"wandb-api-key": wandb_api_key}), **(extra_headers or {})}
        return await self._post(
            "/v1/customization/jobs",
            body=await async_maybe_transform(
                {
                    "config": config,
                    "dataset": dataset,
                    "hyperparameters": hyperparameters,
                    "dataset_parameters": dataset_parameters,
                    "description": description,
                    "integrations": integrations,
                    "name": name,
                    "output_model": output_model,
                    "ownership": ownership,
                    "project": project,
                },
                job_create_params.JobCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CustomizationJobOutput,
        )

    async def retrieve(
        self,
        job_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CustomizationJobOutput:
        """
        Get info about a customization job.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not job_id:
            raise ValueError(f"Expected a non-empty value for `job_id` but received {job_id!r}")
        return await self._get(
            f"/v1/customization/jobs/{job_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CustomizationJobOutput,
        )

    def list(
        self,
        *,
        filter: CustomizationJobListFilterParam | NotGiven = NOT_GIVEN,
        page: int | NotGiven = NOT_GIVEN,
        page_size: int | NotGiven = NOT_GIVEN,
        sort: GenericSortField | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AsyncPaginator[CustomizationJobOutput, AsyncDefaultPagination[CustomizationJobOutput]]:
        """
        List available customization jobs.

        Args:
          filter: Filter jobs on various criteria.

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
            "/v1/customization/jobs",
            page=AsyncDefaultPagination[CustomizationJobOutput],
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
                    job_list_params.JobListParams,
                ),
            ),
            model=CustomizationJobOutput,
        )

    async def cancel(
        self,
        job_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CustomizationJobOutput:
        """
        Cancel a customization job.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not job_id:
            raise ValueError(f"Expected a non-empty value for `job_id` but received {job_id!r}")
        return await self._post(
            f"/v1/customization/jobs/{job_id}/cancel",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CustomizationJobOutput,
        )

    async def container_logs(
        self,
        job_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> JobLogs:
        """
        List the metrics emitted from training.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not job_id:
            raise ValueError(f"Expected a non-empty value for `job_id` but received {job_id!r}")
        return await self._get(
            f"/v1/customization/jobs/{job_id}/container-logs",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=JobLogs,
        )

    async def status(
        self,
        job_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CustomizationStatusDetails:
        """
        List the metrics emitted from training.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not job_id:
            raise ValueError(f"Expected a non-empty value for `job_id` but received {job_id!r}")
        return await self._get(
            f"/v1/customization/jobs/{job_id}/status",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CustomizationStatusDetails,
        )


class JobsResourceWithRawResponse:
    def __init__(self, jobs: JobsResource) -> None:
        self._jobs = jobs

        self.create = to_raw_response_wrapper(
            jobs.create,
        )
        self.retrieve = to_raw_response_wrapper(
            jobs.retrieve,
        )
        self.list = to_raw_response_wrapper(
            jobs.list,
        )
        self.cancel = to_raw_response_wrapper(
            jobs.cancel,
        )
        self.container_logs = to_raw_response_wrapper(
            jobs.container_logs,
        )
        self.status = to_raw_response_wrapper(
            jobs.status,
        )


class AsyncJobsResourceWithRawResponse:
    def __init__(self, jobs: AsyncJobsResource) -> None:
        self._jobs = jobs

        self.create = async_to_raw_response_wrapper(
            jobs.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            jobs.retrieve,
        )
        self.list = async_to_raw_response_wrapper(
            jobs.list,
        )
        self.cancel = async_to_raw_response_wrapper(
            jobs.cancel,
        )
        self.container_logs = async_to_raw_response_wrapper(
            jobs.container_logs,
        )
        self.status = async_to_raw_response_wrapper(
            jobs.status,
        )


class JobsResourceWithStreamingResponse:
    def __init__(self, jobs: JobsResource) -> None:
        self._jobs = jobs

        self.create = to_streamed_response_wrapper(
            jobs.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            jobs.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            jobs.list,
        )
        self.cancel = to_streamed_response_wrapper(
            jobs.cancel,
        )
        self.container_logs = to_streamed_response_wrapper(
            jobs.container_logs,
        )
        self.status = to_streamed_response_wrapper(
            jobs.status,
        )


class AsyncJobsResourceWithStreamingResponse:
    def __init__(self, jobs: AsyncJobsResource) -> None:
        self._jobs = jobs

        self.create = async_to_streamed_response_wrapper(
            jobs.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            jobs.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            jobs.list,
        )
        self.cancel = async_to_streamed_response_wrapper(
            jobs.cancel,
        )
        self.container_logs = async_to_streamed_response_wrapper(
            jobs.container_logs,
        )
        self.status = async_to_streamed_response_wrapper(
            jobs.status,
        )
