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

import os
from typing import TYPE_CHECKING, Any, Union, Mapping
from typing_extensions import Self, override

import httpx

from . import _exceptions
from ._qs import Querystring
from ._types import (
    NOT_GIVEN,
    Omit,
    Timeout,
    NotGiven,
    Transport,
    ProxiesTypes,
    RequestOptions,
)
from ._utils import is_given, get_async_library
from ._compat import cached_property
from ._version import __version__
from ._streaming import Stream as Stream, AsyncStream as AsyncStream
from ._exceptions import APIStatusError
from ._base_client import (
    DEFAULT_MAX_RETRIES,
    SyncAPIClient,
    AsyncAPIClient,
)

if TYPE_CHECKING:
    from .resources import (
        chat,
        models,
        datasets,
        projects,
        guardrail,
        deployment,
        embeddings,
        evaluation,
        namespaces,
        completions,
        customization,
    )
    from .resources.models import ModelsResource, AsyncModelsResource
    from .resources.datasets import DatasetsResource, AsyncDatasetsResource
    from .resources.projects import ProjectsResource, AsyncProjectsResource
    from .resources.chat.chat import ChatResource, AsyncChatResource
    from .lib.custom_resources import inference
    from .resources.embeddings import EmbeddingsResource, AsyncEmbeddingsResource
    from .resources.namespaces import NamespacesResource, AsyncNamespacesResource
    from .resources.completions import CompletionsResource, AsyncCompletionsResource
    from .resources.guardrail.guardrail import GuardrailResource, AsyncGuardrailResource
    from .lib.custom_resources.inference import InferenceResource, AsyncInferenceResource
    from .resources.deployment.deployment import DeploymentResource, AsyncDeploymentResource
    from .resources.evaluation.evaluation import EvaluationResource, AsyncEvaluationResource
    from .resources.customization.customization import CustomizationResource, AsyncCustomizationResource

__all__ = [
    "Timeout",
    "Transport",
    "ProxiesTypes",
    "RequestOptions",
    "NeMoMicroservices",
    "AsyncNeMoMicroservices",
    "Client",
    "AsyncClient",
]


class NeMoMicroservices(SyncAPIClient):
    # client options

    def __init__(
        self,
        *,
        base_url: str | httpx.URL | None = None,
        inference_base_url: str | httpx.URL | None = None,
        timeout: Union[float, Timeout, None, NotGiven] = NOT_GIVEN,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        # Configure a custom httpx client.
        # We provide a `DefaultHttpxClient` class that you can pass to retain the default values we use for `limits`, `timeout` & `follow_redirects`.
        # See the [httpx documentation](https://www.python-httpx.org/api/#client) for more details.
        http_client: httpx.Client | None = None,
        # Enable or disable schema validation for data returned by the API.
        # When enabled an error APIResponseValidationError is raised
        # if the API responds with invalid data for the expected schema.
        #
        # This parameter may be removed or changed in the future.
        # If you rely on this feature, please open a GitHub issue
        # outlining your use-case to help us decide if it should be
        # part of our public interface in the future.
        _strict_response_validation: bool = False,
    ) -> None:
        """Construct a new synchronous NeMoMicroservices client instance."""
        if base_url is None:
            base_url = os.environ.get("NEMO_MICROSERVICES_BASE_URL")
        if base_url is None:
            base_url = f"http://nemo.test/"

        super().__init__(
            version=__version__,
            base_url=base_url,
            max_retries=max_retries,
            timeout=timeout,
            http_client=http_client,
            custom_headers=default_headers,
            custom_query=default_query,
            _strict_response_validation=_strict_response_validation,
        )

        # If no inference_base_url is provided, use base_url
        self.inference_base_url = self._enforce_trailing_slash(httpx.URL(inference_base_url or base_url))

    @cached_property
    def chat(self) -> ChatResource:
        from .resources.chat import ChatResource

        return ChatResource(self)

    @cached_property
    def completions(self) -> CompletionsResource:
        from .resources.completions import CompletionsResource

        return CompletionsResource(self)

    @cached_property
    def embeddings(self) -> EmbeddingsResource:
        from .resources.embeddings import EmbeddingsResource

        return EmbeddingsResource(self)

    @cached_property
    def customization(self) -> CustomizationResource:
        from .resources.customization import CustomizationResource

        return CustomizationResource(self)

    @cached_property
    def datasets(self) -> DatasetsResource:
        from .resources.datasets import DatasetsResource

        return DatasetsResource(self)

    @cached_property
    def deployment(self) -> DeploymentResource:
        from .resources.deployment import DeploymentResource

        return DeploymentResource(self)

    @cached_property
    def evaluation(self) -> EvaluationResource:
        from .resources.evaluation import EvaluationResource

        return EvaluationResource(self)

    @cached_property
    def guardrail(self) -> GuardrailResource:
        from .resources.guardrail import GuardrailResource

        return GuardrailResource(self)

    @cached_property
    def models(self) -> ModelsResource:
        from .resources.models import ModelsResource

        return ModelsResource(self)

    @cached_property
    def namespaces(self) -> NamespacesResource:
        from .resources.namespaces import NamespacesResource

        return NamespacesResource(self)

    @cached_property
    def projects(self) -> ProjectsResource:
        from .resources.projects import ProjectsResource

        return ProjectsResource(self)

    @cached_property
    def inference(self) -> InferenceResource:
        from .lib.custom_resources.inference import InferenceResource

        return InferenceResource(self)

    @cached_property
    def with_raw_response(self) -> NeMoMicroservicesWithRawResponse:
        return NeMoMicroservicesWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> NeMoMicroservicesWithStreamedResponse:
        return NeMoMicroservicesWithStreamedResponse(self)

    @override
    def _prepare_url(self, url: str) -> httpx.URL:
        """
        Merge a URL argument together with any 'base_url' on the client,
        to create the URL used for the outgoing request.

        NOTE: this overrides the BaseClient._prepare_url to account for the inference URL.
        """
        # Copied from httpx's `_merge_url` method.
        merge_url = httpx.URL(url)

        if (
            url == "/v1/completions"
            or url == "/v1/chat/completions"
            or url == "/v1/embeddings"
            or url == "/inference/v1/models"
        ):
            base_url = self.inference_base_url
            if url == "/inference/v1/models":
                merge_url = httpx.URL("/v1/models")
        else:
            base_url = self.base_url

        if merge_url.is_relative_url:
            merge_raw_path = base_url.raw_path + merge_url.raw_path.lstrip(b"/")
            return base_url.copy_with(raw_path=merge_raw_path)

        return merge_url

    @property
    @override
    def qs(self) -> Querystring:
        return Querystring(array_format="comma")

    @property
    @override
    def default_headers(self) -> dict[str, str | Omit]:
        return {
            **super().default_headers,
            "X-Stainless-Async": "false",
            **self._custom_headers,
        }

    def copy(
        self,
        *,
        base_url: str | httpx.URL | None = None,
        inference_base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = NOT_GIVEN,
        http_client: httpx.Client | None = None,
        max_retries: int | NotGiven = NOT_GIVEN,
        default_headers: Mapping[str, str] | None = None,
        set_default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        set_default_query: Mapping[str, object] | None = None,
        _extra_kwargs: Mapping[str, Any] = {},
    ) -> Self:
        """
        Create a new client instance re-using the same options given to the current client with optional overriding.
        """
        if default_headers is not None and set_default_headers is not None:
            raise ValueError("The `default_headers` and `set_default_headers` arguments are mutually exclusive")

        if default_query is not None and set_default_query is not None:
            raise ValueError("The `default_query` and `set_default_query` arguments are mutually exclusive")

        headers = self._custom_headers
        if default_headers is not None:
            headers = {**headers, **default_headers}
        elif set_default_headers is not None:
            headers = set_default_headers

        params = self._custom_query
        if default_query is not None:
            params = {**params, **default_query}
        elif set_default_query is not None:
            params = set_default_query

        http_client = http_client or self._client
        return self.__class__(
            base_url=base_url or self.base_url,
            inference_base_url=inference_base_url or self.inference_base_url,
            timeout=self.timeout if isinstance(timeout, NotGiven) else timeout,
            http_client=http_client,
            max_retries=max_retries if is_given(max_retries) else self.max_retries,
            default_headers=headers,
            default_query=params,
            **_extra_kwargs,
        )

    # Alias for `copy` for nicer inline usage, e.g.
    # client.with_options(timeout=10).foo.create(...)
    with_options = copy

    @override
    def _make_status_error(
        self,
        err_msg: str,
        *,
        body: object,
        response: httpx.Response,
    ) -> APIStatusError:
        if response.status_code == 400:
            return _exceptions.BadRequestError(err_msg, response=response, body=body)

        if response.status_code == 401:
            return _exceptions.AuthenticationError(err_msg, response=response, body=body)

        if response.status_code == 403:
            return _exceptions.PermissionDeniedError(err_msg, response=response, body=body)

        if response.status_code == 404:
            return _exceptions.NotFoundError(err_msg, response=response, body=body)

        if response.status_code == 409:
            return _exceptions.ConflictError(err_msg, response=response, body=body)

        if response.status_code == 422:
            return _exceptions.UnprocessableEntityError(err_msg, response=response, body=body)

        if response.status_code == 429:
            return _exceptions.RateLimitError(err_msg, response=response, body=body)

        if response.status_code >= 500:
            return _exceptions.InternalServerError(err_msg, response=response, body=body)
        return APIStatusError(err_msg, response=response, body=body)


class AsyncNeMoMicroservices(AsyncAPIClient):
    # client options

    def __init__(
        self,
        *,
        base_url: str | httpx.URL | None = None,
        inference_base_url: str | httpx.URL | None = None,
        timeout: Union[float, Timeout, None, NotGiven] = NOT_GIVEN,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        # Configure a custom httpx client.
        # We provide a `DefaultAsyncHttpxClient` class that you can pass to retain the default values we use for `limits`, `timeout` & `follow_redirects`.
        # See the [httpx documentation](https://www.python-httpx.org/api/#asyncclient) for more details.
        http_client: httpx.AsyncClient | None = None,
        # Enable or disable schema validation for data returned by the API.
        # When enabled an error APIResponseValidationError is raised
        # if the API responds with invalid data for the expected schema.
        #
        # This parameter may be removed or changed in the future.
        # If you rely on this feature, please open a GitHub issue
        # outlining your use-case to help us decide if it should be
        # part of our public interface in the future.
        _strict_response_validation: bool = False,
    ) -> None:
        """Construct a new async AsyncNeMoMicroservices client instance."""
        if base_url is None:
            base_url = os.environ.get("NEMO_MICROSERVICES_BASE_URL")
        if base_url is None:
            base_url = f"http://nemo.test/"

        super().__init__(
            version=__version__,
            base_url=base_url,
            max_retries=max_retries,
            timeout=timeout,
            http_client=http_client,
            custom_headers=default_headers,
            custom_query=default_query,
            _strict_response_validation=_strict_response_validation,
        )

        self._default_stream_cls = AsyncStream

        # If no inference_base_url is provided, use base_url
        self.inference_base_url = self._enforce_trailing_slash(httpx.URL(inference_base_url or base_url))

    @cached_property
    def chat(self) -> AsyncChatResource:
        from .resources.chat import AsyncChatResource

        return AsyncChatResource(self)

    @cached_property
    def completions(self) -> AsyncCompletionsResource:
        from .resources.completions import AsyncCompletionsResource

        return AsyncCompletionsResource(self)

    @cached_property
    def embeddings(self) -> AsyncEmbeddingsResource:
        from .resources.embeddings import AsyncEmbeddingsResource

        return AsyncEmbeddingsResource(self)

    @cached_property
    def customization(self) -> AsyncCustomizationResource:
        from .resources.customization import AsyncCustomizationResource

        return AsyncCustomizationResource(self)

    @cached_property
    def datasets(self) -> AsyncDatasetsResource:
        from .resources.datasets import AsyncDatasetsResource

        return AsyncDatasetsResource(self)

    @cached_property
    def deployment(self) -> AsyncDeploymentResource:
        from .resources.deployment import AsyncDeploymentResource

        return AsyncDeploymentResource(self)

    @cached_property
    def evaluation(self) -> AsyncEvaluationResource:
        from .resources.evaluation import AsyncEvaluationResource

        return AsyncEvaluationResource(self)

    @cached_property
    def guardrail(self) -> AsyncGuardrailResource:
        from .resources.guardrail import AsyncGuardrailResource

        return AsyncGuardrailResource(self)

    @cached_property
    def models(self) -> AsyncModelsResource:
        from .resources.models import AsyncModelsResource

        return AsyncModelsResource(self)

    @cached_property
    def namespaces(self) -> AsyncNamespacesResource:
        from .resources.namespaces import AsyncNamespacesResource

        return AsyncNamespacesResource(self)

    @cached_property
    def projects(self) -> AsyncProjectsResource:
        from .resources.projects import AsyncProjectsResource

        return AsyncProjectsResource(self)

    @cached_property
    def inference(self) -> AsyncInferenceResource:
        from .lib.custom_resources.inference import AsyncInferenceResource

        return AsyncInferenceResource(self)

    @cached_property
    def with_raw_response(self) -> AsyncNeMoMicroservicesWithRawResponse:
        return AsyncNeMoMicroservicesWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncNeMoMicroservicesWithStreamedResponse:
        return AsyncNeMoMicroservicesWithStreamedResponse(self)

    @override
    def _prepare_url(self, url: str) -> httpx.URL:
        """
        Merge a URL argument together with any 'base_url' on the client,
        to create the URL used for the outgoing request.

        NOTE: this overrides the BaseClient._prepare_url to account for the inference URL.
        """
        # Copied from httpx's `_merge_url` method.
        merge_url = httpx.URL(url)

        if (
            url == "/v1/completions"
            or url == "/v1/chat/completions"
            or url == "/v1/embeddings"
            or url == "/inference/v1/models"
        ):
            base_url = self.inference_base_url
            if url == "/inference/v1/models":
                merge_url = httpx.URL("/v1/models")
        else:
            base_url = self.base_url

        if merge_url.is_relative_url:
            merge_raw_path = base_url.raw_path + merge_url.raw_path.lstrip(b"/")
            return base_url.copy_with(raw_path=merge_raw_path)

        return merge_url

    @property
    @override
    def qs(self) -> Querystring:
        return Querystring(array_format="comma")

    @property
    @override
    def default_headers(self) -> dict[str, str | Omit]:
        return {
            **super().default_headers,
            "X-Stainless-Async": f"async:{get_async_library()}",
            **self._custom_headers,
        }

    def copy(
        self,
        *,
        base_url: str | httpx.URL | None = None,
        inference_base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = NOT_GIVEN,
        http_client: httpx.AsyncClient | None = None,
        max_retries: int | NotGiven = NOT_GIVEN,
        default_headers: Mapping[str, str] | None = None,
        set_default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        set_default_query: Mapping[str, object] | None = None,
        _extra_kwargs: Mapping[str, Any] = {},
    ) -> Self:
        """
        Create a new client instance re-using the same options given to the current client with optional overriding.
        """
        if default_headers is not None and set_default_headers is not None:
            raise ValueError("The `default_headers` and `set_default_headers` arguments are mutually exclusive")

        if default_query is not None and set_default_query is not None:
            raise ValueError("The `default_query` and `set_default_query` arguments are mutually exclusive")

        headers = self._custom_headers
        if default_headers is not None:
            headers = {**headers, **default_headers}
        elif set_default_headers is not None:
            headers = set_default_headers

        params = self._custom_query
        if default_query is not None:
            params = {**params, **default_query}
        elif set_default_query is not None:
            params = set_default_query

        http_client = http_client or self._client
        return self.__class__(
            base_url=base_url or self.base_url,
            inference_base_url=inference_base_url or self.inference_base_url,
            timeout=self.timeout if isinstance(timeout, NotGiven) else timeout,
            http_client=http_client,
            max_retries=max_retries if is_given(max_retries) else self.max_retries,
            default_headers=headers,
            default_query=params,
            **_extra_kwargs,
        )

    # Alias for `copy` for nicer inline usage, e.g.
    # client.with_options(timeout=10).foo.create(...)
    with_options = copy

    @override
    def _make_status_error(
        self,
        err_msg: str,
        *,
        body: object,
        response: httpx.Response,
    ) -> APIStatusError:
        if response.status_code == 400:
            return _exceptions.BadRequestError(err_msg, response=response, body=body)

        if response.status_code == 401:
            return _exceptions.AuthenticationError(err_msg, response=response, body=body)

        if response.status_code == 403:
            return _exceptions.PermissionDeniedError(err_msg, response=response, body=body)

        if response.status_code == 404:
            return _exceptions.NotFoundError(err_msg, response=response, body=body)

        if response.status_code == 409:
            return _exceptions.ConflictError(err_msg, response=response, body=body)

        if response.status_code == 422:
            return _exceptions.UnprocessableEntityError(err_msg, response=response, body=body)

        if response.status_code == 429:
            return _exceptions.RateLimitError(err_msg, response=response, body=body)

        if response.status_code >= 500:
            return _exceptions.InternalServerError(err_msg, response=response, body=body)
        return APIStatusError(err_msg, response=response, body=body)


class NeMoMicroservicesWithRawResponse:
    _client: NeMoMicroservices

    def __init__(self, client: NeMoMicroservices) -> None:
        self._client = client

    @cached_property
    def chat(self) -> chat.ChatResourceWithRawResponse:
        from .resources.chat import ChatResourceWithRawResponse

        return ChatResourceWithRawResponse(self._client.chat)

    @cached_property
    def completions(self) -> completions.CompletionsResourceWithRawResponse:
        from .resources.completions import CompletionsResourceWithRawResponse

        return CompletionsResourceWithRawResponse(self._client.completions)

    @cached_property
    def embeddings(self) -> embeddings.EmbeddingsResourceWithRawResponse:
        from .resources.embeddings import EmbeddingsResourceWithRawResponse

        return EmbeddingsResourceWithRawResponse(self._client.embeddings)

    @cached_property
    def customization(self) -> customization.CustomizationResourceWithRawResponse:
        from .resources.customization import CustomizationResourceWithRawResponse

        return CustomizationResourceWithRawResponse(self._client.customization)

    @cached_property
    def datasets(self) -> datasets.DatasetsResourceWithRawResponse:
        from .resources.datasets import DatasetsResourceWithRawResponse

        return DatasetsResourceWithRawResponse(self._client.datasets)

    @cached_property
    def deployment(self) -> deployment.DeploymentResourceWithRawResponse:
        from .resources.deployment import DeploymentResourceWithRawResponse

        return DeploymentResourceWithRawResponse(self._client.deployment)

    @cached_property
    def evaluation(self) -> evaluation.EvaluationResourceWithRawResponse:
        from .resources.evaluation import EvaluationResourceWithRawResponse

        return EvaluationResourceWithRawResponse(self._client.evaluation)

    @cached_property
    def guardrail(self) -> guardrail.GuardrailResourceWithRawResponse:
        from .resources.guardrail import GuardrailResourceWithRawResponse

        return GuardrailResourceWithRawResponse(self._client.guardrail)

    @cached_property
    def models(self) -> models.ModelsResourceWithRawResponse:
        from .resources.models import ModelsResourceWithRawResponse

        return ModelsResourceWithRawResponse(self._client.models)

    @cached_property
    def namespaces(self) -> namespaces.NamespacesResourceWithRawResponse:
        from .resources.namespaces import NamespacesResourceWithRawResponse

        return NamespacesResourceWithRawResponse(self._client.namespaces)

    @cached_property
    def projects(self) -> projects.ProjectsResourceWithRawResponse:
        from .resources.projects import ProjectsResourceWithRawResponse

        return ProjectsResourceWithRawResponse(self._client.projects)

    @cached_property
    def inference(self) -> inference.InferenceResourceWithRawResponse:
        from .lib.custom_resources.inference import InferenceResourceWithRawResponse

        return InferenceResourceWithRawResponse(self._client.inference)


class AsyncNeMoMicroservicesWithRawResponse:
    _client: AsyncNeMoMicroservices

    def __init__(self, client: AsyncNeMoMicroservices) -> None:
        self._client = client

    @cached_property
    def chat(self) -> chat.AsyncChatResourceWithRawResponse:
        from .resources.chat import AsyncChatResourceWithRawResponse

        return AsyncChatResourceWithRawResponse(self._client.chat)

    @cached_property
    def completions(self) -> completions.AsyncCompletionsResourceWithRawResponse:
        from .resources.completions import AsyncCompletionsResourceWithRawResponse

        return AsyncCompletionsResourceWithRawResponse(self._client.completions)

    @cached_property
    def embeddings(self) -> embeddings.AsyncEmbeddingsResourceWithRawResponse:
        from .resources.embeddings import AsyncEmbeddingsResourceWithRawResponse

        return AsyncEmbeddingsResourceWithRawResponse(self._client.embeddings)

    @cached_property
    def customization(self) -> customization.AsyncCustomizationResourceWithRawResponse:
        from .resources.customization import AsyncCustomizationResourceWithRawResponse

        return AsyncCustomizationResourceWithRawResponse(self._client.customization)

    @cached_property
    def datasets(self) -> datasets.AsyncDatasetsResourceWithRawResponse:
        from .resources.datasets import AsyncDatasetsResourceWithRawResponse

        return AsyncDatasetsResourceWithRawResponse(self._client.datasets)

    @cached_property
    def deployment(self) -> deployment.AsyncDeploymentResourceWithRawResponse:
        from .resources.deployment import AsyncDeploymentResourceWithRawResponse

        return AsyncDeploymentResourceWithRawResponse(self._client.deployment)

    @cached_property
    def evaluation(self) -> evaluation.AsyncEvaluationResourceWithRawResponse:
        from .resources.evaluation import AsyncEvaluationResourceWithRawResponse

        return AsyncEvaluationResourceWithRawResponse(self._client.evaluation)

    @cached_property
    def guardrail(self) -> guardrail.AsyncGuardrailResourceWithRawResponse:
        from .resources.guardrail import AsyncGuardrailResourceWithRawResponse

        return AsyncGuardrailResourceWithRawResponse(self._client.guardrail)

    @cached_property
    def models(self) -> models.AsyncModelsResourceWithRawResponse:
        from .resources.models import AsyncModelsResourceWithRawResponse

        return AsyncModelsResourceWithRawResponse(self._client.models)

    @cached_property
    def namespaces(self) -> namespaces.AsyncNamespacesResourceWithRawResponse:
        from .resources.namespaces import AsyncNamespacesResourceWithRawResponse

        return AsyncNamespacesResourceWithRawResponse(self._client.namespaces)

    @cached_property
    def projects(self) -> projects.AsyncProjectsResourceWithRawResponse:
        from .resources.projects import AsyncProjectsResourceWithRawResponse

        return AsyncProjectsResourceWithRawResponse(self._client.projects)

    @cached_property
    def inference(self) -> inference.AsyncInferenceResourceWithRawResponse:
        from .lib.custom_resources.inference import AsyncInferenceResourceWithRawResponse

        return AsyncInferenceResourceWithRawResponse(self._client.inference)


class NeMoMicroservicesWithStreamedResponse:
    _client: NeMoMicroservices

    def __init__(self, client: NeMoMicroservices) -> None:
        self._client = client

    @cached_property
    def chat(self) -> chat.ChatResourceWithStreamingResponse:
        from .resources.chat import ChatResourceWithStreamingResponse

        return ChatResourceWithStreamingResponse(self._client.chat)

    @cached_property
    def completions(self) -> completions.CompletionsResourceWithStreamingResponse:
        from .resources.completions import CompletionsResourceWithStreamingResponse

        return CompletionsResourceWithStreamingResponse(self._client.completions)

    @cached_property
    def embeddings(self) -> embeddings.EmbeddingsResourceWithStreamingResponse:
        from .resources.embeddings import EmbeddingsResourceWithStreamingResponse

        return EmbeddingsResourceWithStreamingResponse(self._client.embeddings)

    @cached_property
    def customization(self) -> customization.CustomizationResourceWithStreamingResponse:
        from .resources.customization import CustomizationResourceWithStreamingResponse

        return CustomizationResourceWithStreamingResponse(self._client.customization)

    @cached_property
    def datasets(self) -> datasets.DatasetsResourceWithStreamingResponse:
        from .resources.datasets import DatasetsResourceWithStreamingResponse

        return DatasetsResourceWithStreamingResponse(self._client.datasets)

    @cached_property
    def deployment(self) -> deployment.DeploymentResourceWithStreamingResponse:
        from .resources.deployment import DeploymentResourceWithStreamingResponse

        return DeploymentResourceWithStreamingResponse(self._client.deployment)

    @cached_property
    def evaluation(self) -> evaluation.EvaluationResourceWithStreamingResponse:
        from .resources.evaluation import EvaluationResourceWithStreamingResponse

        return EvaluationResourceWithStreamingResponse(self._client.evaluation)

    @cached_property
    def guardrail(self) -> guardrail.GuardrailResourceWithStreamingResponse:
        from .resources.guardrail import GuardrailResourceWithStreamingResponse

        return GuardrailResourceWithStreamingResponse(self._client.guardrail)

    @cached_property
    def models(self) -> models.ModelsResourceWithStreamingResponse:
        from .resources.models import ModelsResourceWithStreamingResponse

        return ModelsResourceWithStreamingResponse(self._client.models)

    @cached_property
    def namespaces(self) -> namespaces.NamespacesResourceWithStreamingResponse:
        from .resources.namespaces import NamespacesResourceWithStreamingResponse

        return NamespacesResourceWithStreamingResponse(self._client.namespaces)

    @cached_property
    def projects(self) -> projects.ProjectsResourceWithStreamingResponse:
        from .resources.projects import ProjectsResourceWithStreamingResponse

        return ProjectsResourceWithStreamingResponse(self._client.projects)

    @cached_property
    def inference(self) -> inference.InferenceResourceWithStreamingResponse:
        from .lib.custom_resources.inference import InferenceResourceWithStreamingResponse

        return InferenceResourceWithStreamingResponse(self._client.inference)


class AsyncNeMoMicroservicesWithStreamedResponse:
    _client: AsyncNeMoMicroservices

    def __init__(self, client: AsyncNeMoMicroservices) -> None:
        self._client = client

    @cached_property
    def chat(self) -> chat.AsyncChatResourceWithStreamingResponse:
        from .resources.chat import AsyncChatResourceWithStreamingResponse

        return AsyncChatResourceWithStreamingResponse(self._client.chat)

    @cached_property
    def completions(self) -> completions.AsyncCompletionsResourceWithStreamingResponse:
        from .resources.completions import AsyncCompletionsResourceWithStreamingResponse

        return AsyncCompletionsResourceWithStreamingResponse(self._client.completions)

    @cached_property
    def embeddings(self) -> embeddings.AsyncEmbeddingsResourceWithStreamingResponse:
        from .resources.embeddings import AsyncEmbeddingsResourceWithStreamingResponse

        return AsyncEmbeddingsResourceWithStreamingResponse(self._client.embeddings)

    @cached_property
    def customization(self) -> customization.AsyncCustomizationResourceWithStreamingResponse:
        from .resources.customization import AsyncCustomizationResourceWithStreamingResponse

        return AsyncCustomizationResourceWithStreamingResponse(self._client.customization)

    @cached_property
    def datasets(self) -> datasets.AsyncDatasetsResourceWithStreamingResponse:
        from .resources.datasets import AsyncDatasetsResourceWithStreamingResponse

        return AsyncDatasetsResourceWithStreamingResponse(self._client.datasets)

    @cached_property
    def deployment(self) -> deployment.AsyncDeploymentResourceWithStreamingResponse:
        from .resources.deployment import AsyncDeploymentResourceWithStreamingResponse

        return AsyncDeploymentResourceWithStreamingResponse(self._client.deployment)

    @cached_property
    def evaluation(self) -> evaluation.AsyncEvaluationResourceWithStreamingResponse:
        from .resources.evaluation import AsyncEvaluationResourceWithStreamingResponse

        return AsyncEvaluationResourceWithStreamingResponse(self._client.evaluation)

    @cached_property
    def guardrail(self) -> guardrail.AsyncGuardrailResourceWithStreamingResponse:
        from .resources.guardrail import AsyncGuardrailResourceWithStreamingResponse

        return AsyncGuardrailResourceWithStreamingResponse(self._client.guardrail)

    @cached_property
    def models(self) -> models.AsyncModelsResourceWithStreamingResponse:
        from .resources.models import AsyncModelsResourceWithStreamingResponse

        return AsyncModelsResourceWithStreamingResponse(self._client.models)

    @cached_property
    def namespaces(self) -> namespaces.AsyncNamespacesResourceWithStreamingResponse:
        from .resources.namespaces import AsyncNamespacesResourceWithStreamingResponse

        return AsyncNamespacesResourceWithStreamingResponse(self._client.namespaces)

    @cached_property
    def projects(self) -> projects.AsyncProjectsResourceWithStreamingResponse:
        from .resources.projects import AsyncProjectsResourceWithStreamingResponse

        return AsyncProjectsResourceWithStreamingResponse(self._client.projects)

    @cached_property
    def inference(self) -> inference.AsyncInferenceResourceWithStreamingResponse:
        from .lib.custom_resources.inference import AsyncInferenceResourceWithStreamingResponse

        return AsyncInferenceResourceWithStreamingResponse(self._client.inference)


Client = NeMoMicroservices

AsyncClient = AsyncNeMoMicroservices
