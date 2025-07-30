# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from ......_compat import cached_property
from ......_resource import SyncAPIResource, AsyncAPIResource
from .docling_extractor import (
    DoclingExtractorResource,
    AsyncDoclingExtractorResource,
    DoclingExtractorResourceWithRawResponse,
    AsyncDoclingExtractorResourceWithRawResponse,
    DoclingExtractorResourceWithStreamingResponse,
    AsyncDoclingExtractorResourceWithStreamingResponse,
)

__all__ = ["ExtractorResource", "AsyncExtractorResource"]


class ExtractorResource(SyncAPIResource):
    @cached_property
    def docling_extractor(self) -> DoclingExtractorResource:
        return DoclingExtractorResource(self._client)

    @cached_property
    def with_raw_response(self) -> ExtractorResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/quarklabsai/quarkupy#accessing-raw-response-data-eg-headers
        """
        return ExtractorResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ExtractorResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/quarklabsai/quarkupy#with_streaming_response
        """
        return ExtractorResourceWithStreamingResponse(self)


class AsyncExtractorResource(AsyncAPIResource):
    @cached_property
    def docling_extractor(self) -> AsyncDoclingExtractorResource:
        return AsyncDoclingExtractorResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncExtractorResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/quarklabsai/quarkupy#accessing-raw-response-data-eg-headers
        """
        return AsyncExtractorResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncExtractorResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/quarklabsai/quarkupy#with_streaming_response
        """
        return AsyncExtractorResourceWithStreamingResponse(self)


class ExtractorResourceWithRawResponse:
    def __init__(self, extractor: ExtractorResource) -> None:
        self._extractor = extractor

    @cached_property
    def docling_extractor(self) -> DoclingExtractorResourceWithRawResponse:
        return DoclingExtractorResourceWithRawResponse(self._extractor.docling_extractor)


class AsyncExtractorResourceWithRawResponse:
    def __init__(self, extractor: AsyncExtractorResource) -> None:
        self._extractor = extractor

    @cached_property
    def docling_extractor(self) -> AsyncDoclingExtractorResourceWithRawResponse:
        return AsyncDoclingExtractorResourceWithRawResponse(self._extractor.docling_extractor)


class ExtractorResourceWithStreamingResponse:
    def __init__(self, extractor: ExtractorResource) -> None:
        self._extractor = extractor

    @cached_property
    def docling_extractor(self) -> DoclingExtractorResourceWithStreamingResponse:
        return DoclingExtractorResourceWithStreamingResponse(self._extractor.docling_extractor)


class AsyncExtractorResourceWithStreamingResponse:
    def __init__(self, extractor: AsyncExtractorResource) -> None:
        self._extractor = extractor

    @cached_property
    def docling_extractor(self) -> AsyncDoclingExtractorResourceWithStreamingResponse:
        return AsyncDoclingExtractorResourceWithStreamingResponse(self._extractor.docling_extractor)
