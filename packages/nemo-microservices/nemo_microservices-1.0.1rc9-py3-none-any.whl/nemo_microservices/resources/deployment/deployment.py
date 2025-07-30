# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from .configs import (
    ConfigsResource,
    AsyncConfigsResource,
    ConfigsResourceWithRawResponse,
    AsyncConfigsResourceWithRawResponse,
    ConfigsResourceWithStreamingResponse,
    AsyncConfigsResourceWithStreamingResponse,
)
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from .model_deployments import (
    ModelDeploymentsResource,
    AsyncModelDeploymentsResource,
    ModelDeploymentsResourceWithRawResponse,
    AsyncModelDeploymentsResourceWithRawResponse,
    ModelDeploymentsResourceWithStreamingResponse,
    AsyncModelDeploymentsResourceWithStreamingResponse,
)

__all__ = ["DeploymentResource", "AsyncDeploymentResource"]


class DeploymentResource(SyncAPIResource):
    @cached_property
    def configs(self) -> ConfigsResource:
        return ConfigsResource(self._client)

    @cached_property
    def model_deployments(self) -> ModelDeploymentsResource:
        return ModelDeploymentsResource(self._client)

    @cached_property
    def with_raw_response(self) -> DeploymentResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/stainless-sdks/nemo-microservices-v1-python#accessing-raw-response-data-eg-headers
        """
        return DeploymentResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> DeploymentResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/stainless-sdks/nemo-microservices-v1-python#with_streaming_response
        """
        return DeploymentResourceWithStreamingResponse(self)


class AsyncDeploymentResource(AsyncAPIResource):
    @cached_property
    def configs(self) -> AsyncConfigsResource:
        return AsyncConfigsResource(self._client)

    @cached_property
    def model_deployments(self) -> AsyncModelDeploymentsResource:
        return AsyncModelDeploymentsResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncDeploymentResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/stainless-sdks/nemo-microservices-v1-python#accessing-raw-response-data-eg-headers
        """
        return AsyncDeploymentResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncDeploymentResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/stainless-sdks/nemo-microservices-v1-python#with_streaming_response
        """
        return AsyncDeploymentResourceWithStreamingResponse(self)


class DeploymentResourceWithRawResponse:
    def __init__(self, deployment: DeploymentResource) -> None:
        self._deployment = deployment

    @cached_property
    def configs(self) -> ConfigsResourceWithRawResponse:
        return ConfigsResourceWithRawResponse(self._deployment.configs)

    @cached_property
    def model_deployments(self) -> ModelDeploymentsResourceWithRawResponse:
        return ModelDeploymentsResourceWithRawResponse(self._deployment.model_deployments)


class AsyncDeploymentResourceWithRawResponse:
    def __init__(self, deployment: AsyncDeploymentResource) -> None:
        self._deployment = deployment

    @cached_property
    def configs(self) -> AsyncConfigsResourceWithRawResponse:
        return AsyncConfigsResourceWithRawResponse(self._deployment.configs)

    @cached_property
    def model_deployments(self) -> AsyncModelDeploymentsResourceWithRawResponse:
        return AsyncModelDeploymentsResourceWithRawResponse(self._deployment.model_deployments)


class DeploymentResourceWithStreamingResponse:
    def __init__(self, deployment: DeploymentResource) -> None:
        self._deployment = deployment

    @cached_property
    def configs(self) -> ConfigsResourceWithStreamingResponse:
        return ConfigsResourceWithStreamingResponse(self._deployment.configs)

    @cached_property
    def model_deployments(self) -> ModelDeploymentsResourceWithStreamingResponse:
        return ModelDeploymentsResourceWithStreamingResponse(self._deployment.model_deployments)


class AsyncDeploymentResourceWithStreamingResponse:
    def __init__(self, deployment: AsyncDeploymentResource) -> None:
        self._deployment = deployment

    @cached_property
    def configs(self) -> AsyncConfigsResourceWithStreamingResponse:
        return AsyncConfigsResourceWithStreamingResponse(self._deployment.configs)

    @cached_property
    def model_deployments(self) -> AsyncModelDeploymentsResourceWithStreamingResponse:
        return AsyncModelDeploymentsResourceWithStreamingResponse(self._deployment.model_deployments)
