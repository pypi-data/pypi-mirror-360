# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from .agent import (
    AgentResource,
    AsyncAgentResource,
    AgentResourceWithRawResponse,
    AsyncAgentResourceWithRawResponse,
    AgentResourceWithStreamingResponse,
    AsyncAgentResourceWithStreamingResponse,
)
from .source import (
    SourceResource,
    AsyncSourceResource,
    SourceResourceWithRawResponse,
    AsyncSourceResourceWithRawResponse,
    SourceResourceWithStreamingResponse,
    AsyncSourceResourceWithStreamingResponse,
)
from ..._compat import cached_property
from .management import (
    ManagementResource,
    AsyncManagementResource,
    ManagementResourceWithRawResponse,
    AsyncManagementResourceWithRawResponse,
    ManagementResourceWithStreamingResponse,
    AsyncManagementResourceWithStreamingResponse,
)
from ..._resource import SyncAPIResource, AsyncAPIResource
from .context.context import (
    ContextResource,
    AsyncContextResource,
    ContextResourceWithRawResponse,
    AsyncContextResourceWithRawResponse,
    ContextResourceWithStreamingResponse,
    AsyncContextResourceWithStreamingResponse,
)
from .registry.registry import (
    RegistryResource,
    AsyncRegistryResource,
    RegistryResourceWithRawResponse,
    AsyncRegistryResourceWithRawResponse,
    RegistryResourceWithStreamingResponse,
    AsyncRegistryResourceWithStreamingResponse,
)

__all__ = ["WorkerResource", "AsyncWorkerResource"]


class WorkerResource(SyncAPIResource):
    @cached_property
    def management(self) -> ManagementResource:
        return ManagementResource(self._client)

    @cached_property
    def agent(self) -> AgentResource:
        return AgentResource(self._client)

    @cached_property
    def registry(self) -> RegistryResource:
        return RegistryResource(self._client)

    @cached_property
    def source(self) -> SourceResource:
        return SourceResource(self._client)

    @cached_property
    def context(self) -> ContextResource:
        return ContextResource(self._client)

    @cached_property
    def with_raw_response(self) -> WorkerResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/quarklabsai/quarkupy#accessing-raw-response-data-eg-headers
        """
        return WorkerResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> WorkerResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/quarklabsai/quarkupy#with_streaming_response
        """
        return WorkerResourceWithStreamingResponse(self)


class AsyncWorkerResource(AsyncAPIResource):
    @cached_property
    def management(self) -> AsyncManagementResource:
        return AsyncManagementResource(self._client)

    @cached_property
    def agent(self) -> AsyncAgentResource:
        return AsyncAgentResource(self._client)

    @cached_property
    def registry(self) -> AsyncRegistryResource:
        return AsyncRegistryResource(self._client)

    @cached_property
    def source(self) -> AsyncSourceResource:
        return AsyncSourceResource(self._client)

    @cached_property
    def context(self) -> AsyncContextResource:
        return AsyncContextResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncWorkerResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/quarklabsai/quarkupy#accessing-raw-response-data-eg-headers
        """
        return AsyncWorkerResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncWorkerResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/quarklabsai/quarkupy#with_streaming_response
        """
        return AsyncWorkerResourceWithStreamingResponse(self)


class WorkerResourceWithRawResponse:
    def __init__(self, worker: WorkerResource) -> None:
        self._worker = worker

    @cached_property
    def management(self) -> ManagementResourceWithRawResponse:
        return ManagementResourceWithRawResponse(self._worker.management)

    @cached_property
    def agent(self) -> AgentResourceWithRawResponse:
        return AgentResourceWithRawResponse(self._worker.agent)

    @cached_property
    def registry(self) -> RegistryResourceWithRawResponse:
        return RegistryResourceWithRawResponse(self._worker.registry)

    @cached_property
    def source(self) -> SourceResourceWithRawResponse:
        return SourceResourceWithRawResponse(self._worker.source)

    @cached_property
    def context(self) -> ContextResourceWithRawResponse:
        return ContextResourceWithRawResponse(self._worker.context)


class AsyncWorkerResourceWithRawResponse:
    def __init__(self, worker: AsyncWorkerResource) -> None:
        self._worker = worker

    @cached_property
    def management(self) -> AsyncManagementResourceWithRawResponse:
        return AsyncManagementResourceWithRawResponse(self._worker.management)

    @cached_property
    def agent(self) -> AsyncAgentResourceWithRawResponse:
        return AsyncAgentResourceWithRawResponse(self._worker.agent)

    @cached_property
    def registry(self) -> AsyncRegistryResourceWithRawResponse:
        return AsyncRegistryResourceWithRawResponse(self._worker.registry)

    @cached_property
    def source(self) -> AsyncSourceResourceWithRawResponse:
        return AsyncSourceResourceWithRawResponse(self._worker.source)

    @cached_property
    def context(self) -> AsyncContextResourceWithRawResponse:
        return AsyncContextResourceWithRawResponse(self._worker.context)


class WorkerResourceWithStreamingResponse:
    def __init__(self, worker: WorkerResource) -> None:
        self._worker = worker

    @cached_property
    def management(self) -> ManagementResourceWithStreamingResponse:
        return ManagementResourceWithStreamingResponse(self._worker.management)

    @cached_property
    def agent(self) -> AgentResourceWithStreamingResponse:
        return AgentResourceWithStreamingResponse(self._worker.agent)

    @cached_property
    def registry(self) -> RegistryResourceWithStreamingResponse:
        return RegistryResourceWithStreamingResponse(self._worker.registry)

    @cached_property
    def source(self) -> SourceResourceWithStreamingResponse:
        return SourceResourceWithStreamingResponse(self._worker.source)

    @cached_property
    def context(self) -> ContextResourceWithStreamingResponse:
        return ContextResourceWithStreamingResponse(self._worker.context)


class AsyncWorkerResourceWithStreamingResponse:
    def __init__(self, worker: AsyncWorkerResource) -> None:
        self._worker = worker

    @cached_property
    def management(self) -> AsyncManagementResourceWithStreamingResponse:
        return AsyncManagementResourceWithStreamingResponse(self._worker.management)

    @cached_property
    def agent(self) -> AsyncAgentResourceWithStreamingResponse:
        return AsyncAgentResourceWithStreamingResponse(self._worker.agent)

    @cached_property
    def registry(self) -> AsyncRegistryResourceWithStreamingResponse:
        return AsyncRegistryResourceWithStreamingResponse(self._worker.registry)

    @cached_property
    def source(self) -> AsyncSourceResourceWithStreamingResponse:
        return AsyncSourceResourceWithStreamingResponse(self._worker.source)

    @cached_property
    def context(self) -> AsyncContextResourceWithStreamingResponse:
        return AsyncContextResourceWithStreamingResponse(self._worker.context)
