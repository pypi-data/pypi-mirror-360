# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List

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
from ...types.deployment import (
    model_deployment_list_params,
    model_deployment_create_params,
    model_deployment_update_params,
)
from ...types.shared.delete_response import DeleteResponse
from ...types.shared_params.ownership import Ownership
from ...types.shared.generic_sort_field import GenericSortField
from ...types.deployment.model_deployment import ModelDeployment
from ...types.deployment.model_deployment_filter_param import ModelDeploymentFilterParam

__all__ = ["ModelDeploymentsResource", "AsyncModelDeploymentsResource"]


class ModelDeploymentsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ModelDeploymentsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/stainless-sdks/nemo-microservices-v1-python#accessing-raw-response-data-eg-headers
        """
        return ModelDeploymentsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ModelDeploymentsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/stainless-sdks/nemo-microservices-v1-python#with_streaming_response
        """
        return ModelDeploymentsResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        config: model_deployment_create_params.Config,
        async_enabled: bool | NotGiven = NOT_GIVEN,
        custom_fields: object | NotGiven = NOT_GIVEN,
        description: str | NotGiven = NOT_GIVEN,
        models: List[str] | NotGiven = NOT_GIVEN,
        name: str | NotGiven = NOT_GIVEN,
        namespace: str | NotGiven = NOT_GIVEN,
        ownership: Ownership | NotGiven = NOT_GIVEN,
        project: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ModelDeployment:
        """
        Create a new deployment model_deployment.

        Args:
          config: The deployment configuration.

          async_enabled: Whether the async mode is enabled.

          custom_fields: A set of custom fields that the user can define and use for various purposes.

          description: The description of the entity.

          models: The models served by this deployment.

          name: The name of the identity. Must be unique inside the namespace. If not specified,
              it will be the same as the automatically generated id.

          namespace: The if of the namespace of the entity. This can be missing for namespace
              entities or in deployments that don't use namespaces.

          ownership: Information about ownership of an entity.

              If the entity is a namespace, the `access_policies` will typically apply to all
              entities inside the namespace.

          project: The id of project associated with this entity.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/v1/deployment/model-deployments",
            body=maybe_transform(
                {
                    "config": config,
                    "async_enabled": async_enabled,
                    "custom_fields": custom_fields,
                    "description": description,
                    "models": models,
                    "name": name,
                    "namespace": namespace,
                    "ownership": ownership,
                    "project": project,
                },
                model_deployment_create_params.ModelDeploymentCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ModelDeployment,
        )

    def retrieve(
        self,
        deployment_name: str,
        *,
        namespace: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ModelDeployment:
        """
        Get info about a model deployment.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not namespace:
            raise ValueError(f"Expected a non-empty value for `namespace` but received {namespace!r}")
        if not deployment_name:
            raise ValueError(f"Expected a non-empty value for `deployment_name` but received {deployment_name!r}")
        return self._get(
            f"/v1/deployment/model-deployments/{namespace}/{deployment_name}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ModelDeployment,
        )

    def update(
        self,
        deployment_name: str,
        *,
        namespace: str,
        async_enabled: bool | NotGiven = NOT_GIVEN,
        config: model_deployment_update_params.Config | NotGiven = NOT_GIVEN,
        custom_fields: object | NotGiven = NOT_GIVEN,
        description: str | NotGiven = NOT_GIVEN,
        models: List[str] | NotGiven = NOT_GIVEN,
        ownership: Ownership | NotGiven = NOT_GIVEN,
        project: str | NotGiven = NOT_GIVEN,
        schema_version: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ModelDeployment:
        """
        Update model deployment

        Args:
          async_enabled: Whether the async mode is enabled.

          config: The deployment configuration.

          custom_fields: A set of custom fields that the user can define and use for various purposes.

          description: The description of the entity.

          models: The models served by this deployment.

          ownership: Information about ownership of an entity.

              If the entity is a namespace, the `access_policies` will typically apply to all
              entities inside the namespace.

          project: The id of project associated with this entity.

          schema_version: The version of the schema for the object. Internal use only.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not namespace:
            raise ValueError(f"Expected a non-empty value for `namespace` but received {namespace!r}")
        if not deployment_name:
            raise ValueError(f"Expected a non-empty value for `deployment_name` but received {deployment_name!r}")
        return self._patch(
            f"/v1/deployment/model-deployments/{namespace}/{deployment_name}",
            body=maybe_transform(
                {
                    "async_enabled": async_enabled,
                    "config": config,
                    "custom_fields": custom_fields,
                    "description": description,
                    "models": models,
                    "ownership": ownership,
                    "project": project,
                    "schema_version": schema_version,
                },
                model_deployment_update_params.ModelDeploymentUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ModelDeployment,
        )

    def list(
        self,
        *,
        filter: ModelDeploymentFilterParam | NotGiven = NOT_GIVEN,
        page: int | NotGiven = NOT_GIVEN,
        page_size: int | NotGiven = NOT_GIVEN,
        sort: GenericSortField | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SyncDefaultPagination[ModelDeployment]:
        """
        List available deployment model_deployments.

        Args:
          filter: Filter model_deployments on various criteria.

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
            "/v1/deployment/model-deployments",
            page=SyncDefaultPagination[ModelDeployment],
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
                    model_deployment_list_params.ModelDeploymentListParams,
                ),
            ),
            model=ModelDeployment,
        )

    def delete(
        self,
        deployment_name: str,
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
        Delete Model Deployment

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not namespace:
            raise ValueError(f"Expected a non-empty value for `namespace` but received {namespace!r}")
        if not deployment_name:
            raise ValueError(f"Expected a non-empty value for `deployment_name` but received {deployment_name!r}")
        return self._delete(
            f"/v1/deployment/model-deployments/{namespace}/{deployment_name}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DeleteResponse,
        )


class AsyncModelDeploymentsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncModelDeploymentsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/stainless-sdks/nemo-microservices-v1-python#accessing-raw-response-data-eg-headers
        """
        return AsyncModelDeploymentsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncModelDeploymentsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/stainless-sdks/nemo-microservices-v1-python#with_streaming_response
        """
        return AsyncModelDeploymentsResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        config: model_deployment_create_params.Config,
        async_enabled: bool | NotGiven = NOT_GIVEN,
        custom_fields: object | NotGiven = NOT_GIVEN,
        description: str | NotGiven = NOT_GIVEN,
        models: List[str] | NotGiven = NOT_GIVEN,
        name: str | NotGiven = NOT_GIVEN,
        namespace: str | NotGiven = NOT_GIVEN,
        ownership: Ownership | NotGiven = NOT_GIVEN,
        project: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ModelDeployment:
        """
        Create a new deployment model_deployment.

        Args:
          config: The deployment configuration.

          async_enabled: Whether the async mode is enabled.

          custom_fields: A set of custom fields that the user can define and use for various purposes.

          description: The description of the entity.

          models: The models served by this deployment.

          name: The name of the identity. Must be unique inside the namespace. If not specified,
              it will be the same as the automatically generated id.

          namespace: The if of the namespace of the entity. This can be missing for namespace
              entities or in deployments that don't use namespaces.

          ownership: Information about ownership of an entity.

              If the entity is a namespace, the `access_policies` will typically apply to all
              entities inside the namespace.

          project: The id of project associated with this entity.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/v1/deployment/model-deployments",
            body=await async_maybe_transform(
                {
                    "config": config,
                    "async_enabled": async_enabled,
                    "custom_fields": custom_fields,
                    "description": description,
                    "models": models,
                    "name": name,
                    "namespace": namespace,
                    "ownership": ownership,
                    "project": project,
                },
                model_deployment_create_params.ModelDeploymentCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ModelDeployment,
        )

    async def retrieve(
        self,
        deployment_name: str,
        *,
        namespace: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ModelDeployment:
        """
        Get info about a model deployment.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not namespace:
            raise ValueError(f"Expected a non-empty value for `namespace` but received {namespace!r}")
        if not deployment_name:
            raise ValueError(f"Expected a non-empty value for `deployment_name` but received {deployment_name!r}")
        return await self._get(
            f"/v1/deployment/model-deployments/{namespace}/{deployment_name}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ModelDeployment,
        )

    async def update(
        self,
        deployment_name: str,
        *,
        namespace: str,
        async_enabled: bool | NotGiven = NOT_GIVEN,
        config: model_deployment_update_params.Config | NotGiven = NOT_GIVEN,
        custom_fields: object | NotGiven = NOT_GIVEN,
        description: str | NotGiven = NOT_GIVEN,
        models: List[str] | NotGiven = NOT_GIVEN,
        ownership: Ownership | NotGiven = NOT_GIVEN,
        project: str | NotGiven = NOT_GIVEN,
        schema_version: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ModelDeployment:
        """
        Update model deployment

        Args:
          async_enabled: Whether the async mode is enabled.

          config: The deployment configuration.

          custom_fields: A set of custom fields that the user can define and use for various purposes.

          description: The description of the entity.

          models: The models served by this deployment.

          ownership: Information about ownership of an entity.

              If the entity is a namespace, the `access_policies` will typically apply to all
              entities inside the namespace.

          project: The id of project associated with this entity.

          schema_version: The version of the schema for the object. Internal use only.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not namespace:
            raise ValueError(f"Expected a non-empty value for `namespace` but received {namespace!r}")
        if not deployment_name:
            raise ValueError(f"Expected a non-empty value for `deployment_name` but received {deployment_name!r}")
        return await self._patch(
            f"/v1/deployment/model-deployments/{namespace}/{deployment_name}",
            body=await async_maybe_transform(
                {
                    "async_enabled": async_enabled,
                    "config": config,
                    "custom_fields": custom_fields,
                    "description": description,
                    "models": models,
                    "ownership": ownership,
                    "project": project,
                    "schema_version": schema_version,
                },
                model_deployment_update_params.ModelDeploymentUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ModelDeployment,
        )

    def list(
        self,
        *,
        filter: ModelDeploymentFilterParam | NotGiven = NOT_GIVEN,
        page: int | NotGiven = NOT_GIVEN,
        page_size: int | NotGiven = NOT_GIVEN,
        sort: GenericSortField | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AsyncPaginator[ModelDeployment, AsyncDefaultPagination[ModelDeployment]]:
        """
        List available deployment model_deployments.

        Args:
          filter: Filter model_deployments on various criteria.

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
            "/v1/deployment/model-deployments",
            page=AsyncDefaultPagination[ModelDeployment],
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
                    model_deployment_list_params.ModelDeploymentListParams,
                ),
            ),
            model=ModelDeployment,
        )

    async def delete(
        self,
        deployment_name: str,
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
        Delete Model Deployment

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not namespace:
            raise ValueError(f"Expected a non-empty value for `namespace` but received {namespace!r}")
        if not deployment_name:
            raise ValueError(f"Expected a non-empty value for `deployment_name` but received {deployment_name!r}")
        return await self._delete(
            f"/v1/deployment/model-deployments/{namespace}/{deployment_name}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DeleteResponse,
        )


class ModelDeploymentsResourceWithRawResponse:
    def __init__(self, model_deployments: ModelDeploymentsResource) -> None:
        self._model_deployments = model_deployments

        self.create = to_raw_response_wrapper(
            model_deployments.create,
        )
        self.retrieve = to_raw_response_wrapper(
            model_deployments.retrieve,
        )
        self.update = to_raw_response_wrapper(
            model_deployments.update,
        )
        self.list = to_raw_response_wrapper(
            model_deployments.list,
        )
        self.delete = to_raw_response_wrapper(
            model_deployments.delete,
        )


class AsyncModelDeploymentsResourceWithRawResponse:
    def __init__(self, model_deployments: AsyncModelDeploymentsResource) -> None:
        self._model_deployments = model_deployments

        self.create = async_to_raw_response_wrapper(
            model_deployments.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            model_deployments.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            model_deployments.update,
        )
        self.list = async_to_raw_response_wrapper(
            model_deployments.list,
        )
        self.delete = async_to_raw_response_wrapper(
            model_deployments.delete,
        )


class ModelDeploymentsResourceWithStreamingResponse:
    def __init__(self, model_deployments: ModelDeploymentsResource) -> None:
        self._model_deployments = model_deployments

        self.create = to_streamed_response_wrapper(
            model_deployments.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            model_deployments.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            model_deployments.update,
        )
        self.list = to_streamed_response_wrapper(
            model_deployments.list,
        )
        self.delete = to_streamed_response_wrapper(
            model_deployments.delete,
        )


class AsyncModelDeploymentsResourceWithStreamingResponse:
    def __init__(self, model_deployments: AsyncModelDeploymentsResource) -> None:
        self._model_deployments = model_deployments

        self.create = async_to_streamed_response_wrapper(
            model_deployments.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            model_deployments.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            model_deployments.update,
        )
        self.list = async_to_streamed_response_wrapper(
            model_deployments.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            model_deployments.delete,
        )
