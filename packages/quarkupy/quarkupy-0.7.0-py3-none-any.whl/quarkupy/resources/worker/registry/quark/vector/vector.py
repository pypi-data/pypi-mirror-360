# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from ......_compat import cached_property
from ......_resource import SyncAPIResource, AsyncAPIResource
from .lancedb_ingest import (
    LancedbIngestResource,
    AsyncLancedbIngestResource,
    LancedbIngestResourceWithRawResponse,
    AsyncLancedbIngestResourceWithRawResponse,
    LancedbIngestResourceWithStreamingResponse,
    AsyncLancedbIngestResourceWithStreamingResponse,
)
from .lancedb_search import (
    LancedbSearchResource,
    AsyncLancedbSearchResource,
    LancedbSearchResourceWithRawResponse,
    AsyncLancedbSearchResourceWithRawResponse,
    LancedbSearchResourceWithStreamingResponse,
    AsyncLancedbSearchResourceWithStreamingResponse,
)

__all__ = ["VectorResource", "AsyncVectorResource"]


class VectorResource(SyncAPIResource):
    @cached_property
    def lancedb_ingest(self) -> LancedbIngestResource:
        return LancedbIngestResource(self._client)

    @cached_property
    def lancedb_search(self) -> LancedbSearchResource:
        return LancedbSearchResource(self._client)

    @cached_property
    def with_raw_response(self) -> VectorResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/quarklabsai/quarkupy#accessing-raw-response-data-eg-headers
        """
        return VectorResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> VectorResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/quarklabsai/quarkupy#with_streaming_response
        """
        return VectorResourceWithStreamingResponse(self)


class AsyncVectorResource(AsyncAPIResource):
    @cached_property
    def lancedb_ingest(self) -> AsyncLancedbIngestResource:
        return AsyncLancedbIngestResource(self._client)

    @cached_property
    def lancedb_search(self) -> AsyncLancedbSearchResource:
        return AsyncLancedbSearchResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncVectorResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/quarklabsai/quarkupy#accessing-raw-response-data-eg-headers
        """
        return AsyncVectorResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncVectorResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/quarklabsai/quarkupy#with_streaming_response
        """
        return AsyncVectorResourceWithStreamingResponse(self)


class VectorResourceWithRawResponse:
    def __init__(self, vector: VectorResource) -> None:
        self._vector = vector

    @cached_property
    def lancedb_ingest(self) -> LancedbIngestResourceWithRawResponse:
        return LancedbIngestResourceWithRawResponse(self._vector.lancedb_ingest)

    @cached_property
    def lancedb_search(self) -> LancedbSearchResourceWithRawResponse:
        return LancedbSearchResourceWithRawResponse(self._vector.lancedb_search)


class AsyncVectorResourceWithRawResponse:
    def __init__(self, vector: AsyncVectorResource) -> None:
        self._vector = vector

    @cached_property
    def lancedb_ingest(self) -> AsyncLancedbIngestResourceWithRawResponse:
        return AsyncLancedbIngestResourceWithRawResponse(self._vector.lancedb_ingest)

    @cached_property
    def lancedb_search(self) -> AsyncLancedbSearchResourceWithRawResponse:
        return AsyncLancedbSearchResourceWithRawResponse(self._vector.lancedb_search)


class VectorResourceWithStreamingResponse:
    def __init__(self, vector: VectorResource) -> None:
        self._vector = vector

    @cached_property
    def lancedb_ingest(self) -> LancedbIngestResourceWithStreamingResponse:
        return LancedbIngestResourceWithStreamingResponse(self._vector.lancedb_ingest)

    @cached_property
    def lancedb_search(self) -> LancedbSearchResourceWithStreamingResponse:
        return LancedbSearchResourceWithStreamingResponse(self._vector.lancedb_search)


class AsyncVectorResourceWithStreamingResponse:
    def __init__(self, vector: AsyncVectorResource) -> None:
        self._vector = vector

    @cached_property
    def lancedb_ingest(self) -> AsyncLancedbIngestResourceWithStreamingResponse:
        return AsyncLancedbIngestResourceWithStreamingResponse(self._vector.lancedb_ingest)

    @cached_property
    def lancedb_search(self) -> AsyncLancedbSearchResourceWithStreamingResponse:
        return AsyncLancedbSearchResourceWithStreamingResponse(self._vector.lancedb_search)
