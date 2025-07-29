# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from ......_compat import cached_property
from ......_resource import SyncAPIResource, AsyncAPIResource
from .context_insert_objects import (
    ContextInsertObjectsResource,
    AsyncContextInsertObjectsResource,
    ContextInsertObjectsResourceWithRawResponse,
    AsyncContextInsertObjectsResourceWithRawResponse,
    ContextInsertObjectsResourceWithStreamingResponse,
    AsyncContextInsertObjectsResourceWithStreamingResponse,
)
from .context_insert_segments import (
    ContextInsertSegmentsResource,
    AsyncContextInsertSegmentsResource,
    ContextInsertSegmentsResourceWithRawResponse,
    AsyncContextInsertSegmentsResourceWithRawResponse,
    ContextInsertSegmentsResourceWithStreamingResponse,
    AsyncContextInsertSegmentsResourceWithStreamingResponse,
)
from .context_insert_extracted_segments import (
    ContextInsertExtractedSegmentsResource,
    AsyncContextInsertExtractedSegmentsResource,
    ContextInsertExtractedSegmentsResourceWithRawResponse,
    AsyncContextInsertExtractedSegmentsResourceWithRawResponse,
    ContextInsertExtractedSegmentsResourceWithStreamingResponse,
    AsyncContextInsertExtractedSegmentsResourceWithStreamingResponse,
)
from .context_insert_classified_segments import (
    ContextInsertClassifiedSegmentsResource,
    AsyncContextInsertClassifiedSegmentsResource,
    ContextInsertClassifiedSegmentsResourceWithRawResponse,
    AsyncContextInsertClassifiedSegmentsResourceWithRawResponse,
    ContextInsertClassifiedSegmentsResourceWithStreamingResponse,
    AsyncContextInsertClassifiedSegmentsResourceWithStreamingResponse,
)

__all__ = ["OtherResource", "AsyncOtherResource"]


class OtherResource(SyncAPIResource):
    @cached_property
    def context_insert_objects(self) -> ContextInsertObjectsResource:
        return ContextInsertObjectsResource(self._client)

    @cached_property
    def context_insert_segments(self) -> ContextInsertSegmentsResource:
        return ContextInsertSegmentsResource(self._client)

    @cached_property
    def context_insert_classified_segments(self) -> ContextInsertClassifiedSegmentsResource:
        return ContextInsertClassifiedSegmentsResource(self._client)

    @cached_property
    def context_insert_extracted_segments(self) -> ContextInsertExtractedSegmentsResource:
        return ContextInsertExtractedSegmentsResource(self._client)

    @cached_property
    def with_raw_response(self) -> OtherResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/quarklabsai/quarkupy#accessing-raw-response-data-eg-headers
        """
        return OtherResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> OtherResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/quarklabsai/quarkupy#with_streaming_response
        """
        return OtherResourceWithStreamingResponse(self)


class AsyncOtherResource(AsyncAPIResource):
    @cached_property
    def context_insert_objects(self) -> AsyncContextInsertObjectsResource:
        return AsyncContextInsertObjectsResource(self._client)

    @cached_property
    def context_insert_segments(self) -> AsyncContextInsertSegmentsResource:
        return AsyncContextInsertSegmentsResource(self._client)

    @cached_property
    def context_insert_classified_segments(self) -> AsyncContextInsertClassifiedSegmentsResource:
        return AsyncContextInsertClassifiedSegmentsResource(self._client)

    @cached_property
    def context_insert_extracted_segments(self) -> AsyncContextInsertExtractedSegmentsResource:
        return AsyncContextInsertExtractedSegmentsResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncOtherResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/quarklabsai/quarkupy#accessing-raw-response-data-eg-headers
        """
        return AsyncOtherResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncOtherResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/quarklabsai/quarkupy#with_streaming_response
        """
        return AsyncOtherResourceWithStreamingResponse(self)


class OtherResourceWithRawResponse:
    def __init__(self, other: OtherResource) -> None:
        self._other = other

    @cached_property
    def context_insert_objects(self) -> ContextInsertObjectsResourceWithRawResponse:
        return ContextInsertObjectsResourceWithRawResponse(self._other.context_insert_objects)

    @cached_property
    def context_insert_segments(self) -> ContextInsertSegmentsResourceWithRawResponse:
        return ContextInsertSegmentsResourceWithRawResponse(self._other.context_insert_segments)

    @cached_property
    def context_insert_classified_segments(self) -> ContextInsertClassifiedSegmentsResourceWithRawResponse:
        return ContextInsertClassifiedSegmentsResourceWithRawResponse(self._other.context_insert_classified_segments)

    @cached_property
    def context_insert_extracted_segments(self) -> ContextInsertExtractedSegmentsResourceWithRawResponse:
        return ContextInsertExtractedSegmentsResourceWithRawResponse(self._other.context_insert_extracted_segments)


class AsyncOtherResourceWithRawResponse:
    def __init__(self, other: AsyncOtherResource) -> None:
        self._other = other

    @cached_property
    def context_insert_objects(self) -> AsyncContextInsertObjectsResourceWithRawResponse:
        return AsyncContextInsertObjectsResourceWithRawResponse(self._other.context_insert_objects)

    @cached_property
    def context_insert_segments(self) -> AsyncContextInsertSegmentsResourceWithRawResponse:
        return AsyncContextInsertSegmentsResourceWithRawResponse(self._other.context_insert_segments)

    @cached_property
    def context_insert_classified_segments(self) -> AsyncContextInsertClassifiedSegmentsResourceWithRawResponse:
        return AsyncContextInsertClassifiedSegmentsResourceWithRawResponse(
            self._other.context_insert_classified_segments
        )

    @cached_property
    def context_insert_extracted_segments(self) -> AsyncContextInsertExtractedSegmentsResourceWithRawResponse:
        return AsyncContextInsertExtractedSegmentsResourceWithRawResponse(self._other.context_insert_extracted_segments)


class OtherResourceWithStreamingResponse:
    def __init__(self, other: OtherResource) -> None:
        self._other = other

    @cached_property
    def context_insert_objects(self) -> ContextInsertObjectsResourceWithStreamingResponse:
        return ContextInsertObjectsResourceWithStreamingResponse(self._other.context_insert_objects)

    @cached_property
    def context_insert_segments(self) -> ContextInsertSegmentsResourceWithStreamingResponse:
        return ContextInsertSegmentsResourceWithStreamingResponse(self._other.context_insert_segments)

    @cached_property
    def context_insert_classified_segments(self) -> ContextInsertClassifiedSegmentsResourceWithStreamingResponse:
        return ContextInsertClassifiedSegmentsResourceWithStreamingResponse(
            self._other.context_insert_classified_segments
        )

    @cached_property
    def context_insert_extracted_segments(self) -> ContextInsertExtractedSegmentsResourceWithStreamingResponse:
        return ContextInsertExtractedSegmentsResourceWithStreamingResponse(
            self._other.context_insert_extracted_segments
        )


class AsyncOtherResourceWithStreamingResponse:
    def __init__(self, other: AsyncOtherResource) -> None:
        self._other = other

    @cached_property
    def context_insert_objects(self) -> AsyncContextInsertObjectsResourceWithStreamingResponse:
        return AsyncContextInsertObjectsResourceWithStreamingResponse(self._other.context_insert_objects)

    @cached_property
    def context_insert_segments(self) -> AsyncContextInsertSegmentsResourceWithStreamingResponse:
        return AsyncContextInsertSegmentsResourceWithStreamingResponse(self._other.context_insert_segments)

    @cached_property
    def context_insert_classified_segments(self) -> AsyncContextInsertClassifiedSegmentsResourceWithStreamingResponse:
        return AsyncContextInsertClassifiedSegmentsResourceWithStreamingResponse(
            self._other.context_insert_classified_segments
        )

    @cached_property
    def context_insert_extracted_segments(self) -> AsyncContextInsertExtractedSegmentsResourceWithStreamingResponse:
        return AsyncContextInsertExtractedSegmentsResourceWithStreamingResponse(
            self._other.context_insert_extracted_segments
        )
