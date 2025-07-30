# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from ..._compat import cached_property
from .extractors import (
    ExtractorsResource,
    AsyncExtractorsResource,
    ExtractorsResourceWithRawResponse,
    AsyncExtractorsResourceWithRawResponse,
    ExtractorsResourceWithStreamingResponse,
    AsyncExtractorsResourceWithStreamingResponse,
)
from ..._resource import SyncAPIResource, AsyncAPIResource
from .classifiers import (
    ClassifiersResource,
    AsyncClassifiersResource,
    ClassifiersResourceWithRawResponse,
    AsyncClassifiersResourceWithRawResponse,
    ClassifiersResourceWithStreamingResponse,
    AsyncClassifiersResourceWithStreamingResponse,
)

__all__ = ["ContextResource", "AsyncContextResource"]


class ContextResource(SyncAPIResource):
    @cached_property
    def extractors(self) -> ExtractorsResource:
        return ExtractorsResource(self._client)

    @cached_property
    def classifiers(self) -> ClassifiersResource:
        return ClassifiersResource(self._client)

    @cached_property
    def with_raw_response(self) -> ContextResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/quarklabsai/quarkupy#accessing-raw-response-data-eg-headers
        """
        return ContextResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ContextResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/quarklabsai/quarkupy#with_streaming_response
        """
        return ContextResourceWithStreamingResponse(self)


class AsyncContextResource(AsyncAPIResource):
    @cached_property
    def extractors(self) -> AsyncExtractorsResource:
        return AsyncExtractorsResource(self._client)

    @cached_property
    def classifiers(self) -> AsyncClassifiersResource:
        return AsyncClassifiersResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncContextResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/quarklabsai/quarkupy#accessing-raw-response-data-eg-headers
        """
        return AsyncContextResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncContextResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/quarklabsai/quarkupy#with_streaming_response
        """
        return AsyncContextResourceWithStreamingResponse(self)


class ContextResourceWithRawResponse:
    def __init__(self, context: ContextResource) -> None:
        self._context = context

    @cached_property
    def extractors(self) -> ExtractorsResourceWithRawResponse:
        return ExtractorsResourceWithRawResponse(self._context.extractors)

    @cached_property
    def classifiers(self) -> ClassifiersResourceWithRawResponse:
        return ClassifiersResourceWithRawResponse(self._context.classifiers)


class AsyncContextResourceWithRawResponse:
    def __init__(self, context: AsyncContextResource) -> None:
        self._context = context

    @cached_property
    def extractors(self) -> AsyncExtractorsResourceWithRawResponse:
        return AsyncExtractorsResourceWithRawResponse(self._context.extractors)

    @cached_property
    def classifiers(self) -> AsyncClassifiersResourceWithRawResponse:
        return AsyncClassifiersResourceWithRawResponse(self._context.classifiers)


class ContextResourceWithStreamingResponse:
    def __init__(self, context: ContextResource) -> None:
        self._context = context

    @cached_property
    def extractors(self) -> ExtractorsResourceWithStreamingResponse:
        return ExtractorsResourceWithStreamingResponse(self._context.extractors)

    @cached_property
    def classifiers(self) -> ClassifiersResourceWithStreamingResponse:
        return ClassifiersResourceWithStreamingResponse(self._context.classifiers)


class AsyncContextResourceWithStreamingResponse:
    def __init__(self, context: AsyncContextResource) -> None:
        self._context = context

    @cached_property
    def extractors(self) -> AsyncExtractorsResourceWithStreamingResponse:
        return AsyncExtractorsResourceWithStreamingResponse(self._context.extractors)

    @cached_property
    def classifiers(self) -> AsyncClassifiersResourceWithStreamingResponse:
        return AsyncClassifiersResourceWithStreamingResponse(self._context.classifiers)
