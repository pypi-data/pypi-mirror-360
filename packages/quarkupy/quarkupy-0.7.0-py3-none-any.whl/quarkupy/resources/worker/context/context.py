# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ...._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ...._utils import maybe_transform, async_maybe_transform
from ...._compat import cached_property
from .extractors import (
    ExtractorsResource,
    AsyncExtractorsResource,
    ExtractorsResourceWithRawResponse,
    AsyncExtractorsResourceWithRawResponse,
    ExtractorsResourceWithStreamingResponse,
    AsyncExtractorsResourceWithStreamingResponse,
)
from .classifiers import (
    ClassifiersResource,
    AsyncClassifiersResource,
    ClassifiersResourceWithRawResponse,
    AsyncClassifiersResourceWithRawResponse,
    ClassifiersResourceWithStreamingResponse,
    AsyncClassifiersResourceWithStreamingResponse,
)
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._response import (
    BinaryAPIResponse,
    AsyncBinaryAPIResponse,
    StreamedBinaryAPIResponse,
    AsyncStreamedBinaryAPIResponse,
    to_custom_raw_response_wrapper,
    to_custom_streamed_response_wrapper,
    async_to_custom_raw_response_wrapper,
    async_to_custom_streamed_response_wrapper,
)
from ...._base_client import make_request_options
from ....types.worker import context_retrieve_files_params

__all__ = ["ContextResource", "AsyncContextResource"]


class ContextResource(SyncAPIResource):
    @cached_property
    def classifiers(self) -> ClassifiersResource:
        return ClassifiersResource(self._client)

    @cached_property
    def extractors(self) -> ExtractorsResource:
        return ExtractorsResource(self._client)

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

    def retrieve_files(
        self,
        *,
        limit: int | NotGiven = NOT_GIVEN,
        offset: int | NotGiven = NOT_GIVEN,
        source_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> BinaryAPIResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "application/x-apache-arrow-stream", **(extra_headers or {})}
        return self._get(
            "/worker/context/files",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "limit": limit,
                        "offset": offset,
                        "source_id": source_id,
                    },
                    context_retrieve_files_params.ContextRetrieveFilesParams,
                ),
            ),
            cast_to=BinaryAPIResponse,
        )


class AsyncContextResource(AsyncAPIResource):
    @cached_property
    def classifiers(self) -> AsyncClassifiersResource:
        return AsyncClassifiersResource(self._client)

    @cached_property
    def extractors(self) -> AsyncExtractorsResource:
        return AsyncExtractorsResource(self._client)

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

    async def retrieve_files(
        self,
        *,
        limit: int | NotGiven = NOT_GIVEN,
        offset: int | NotGiven = NOT_GIVEN,
        source_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AsyncBinaryAPIResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "application/x-apache-arrow-stream", **(extra_headers or {})}
        return await self._get(
            "/worker/context/files",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "limit": limit,
                        "offset": offset,
                        "source_id": source_id,
                    },
                    context_retrieve_files_params.ContextRetrieveFilesParams,
                ),
            ),
            cast_to=AsyncBinaryAPIResponse,
        )


class ContextResourceWithRawResponse:
    def __init__(self, context: ContextResource) -> None:
        self._context = context

        self.retrieve_files = to_custom_raw_response_wrapper(
            context.retrieve_files,
            BinaryAPIResponse,
        )

    @cached_property
    def classifiers(self) -> ClassifiersResourceWithRawResponse:
        return ClassifiersResourceWithRawResponse(self._context.classifiers)

    @cached_property
    def extractors(self) -> ExtractorsResourceWithRawResponse:
        return ExtractorsResourceWithRawResponse(self._context.extractors)


class AsyncContextResourceWithRawResponse:
    def __init__(self, context: AsyncContextResource) -> None:
        self._context = context

        self.retrieve_files = async_to_custom_raw_response_wrapper(
            context.retrieve_files,
            AsyncBinaryAPIResponse,
        )

    @cached_property
    def classifiers(self) -> AsyncClassifiersResourceWithRawResponse:
        return AsyncClassifiersResourceWithRawResponse(self._context.classifiers)

    @cached_property
    def extractors(self) -> AsyncExtractorsResourceWithRawResponse:
        return AsyncExtractorsResourceWithRawResponse(self._context.extractors)


class ContextResourceWithStreamingResponse:
    def __init__(self, context: ContextResource) -> None:
        self._context = context

        self.retrieve_files = to_custom_streamed_response_wrapper(
            context.retrieve_files,
            StreamedBinaryAPIResponse,
        )

    @cached_property
    def classifiers(self) -> ClassifiersResourceWithStreamingResponse:
        return ClassifiersResourceWithStreamingResponse(self._context.classifiers)

    @cached_property
    def extractors(self) -> ExtractorsResourceWithStreamingResponse:
        return ExtractorsResourceWithStreamingResponse(self._context.extractors)


class AsyncContextResourceWithStreamingResponse:
    def __init__(self, context: AsyncContextResource) -> None:
        self._context = context

        self.retrieve_files = async_to_custom_streamed_response_wrapper(
            context.retrieve_files,
            AsyncStreamedBinaryAPIResponse,
        )

    @cached_property
    def classifiers(self) -> AsyncClassifiersResourceWithStreamingResponse:
        return AsyncClassifiersResourceWithStreamingResponse(self._context.classifiers)

    @cached_property
    def extractors(self) -> AsyncExtractorsResourceWithStreamingResponse:
        return AsyncExtractorsResourceWithStreamingResponse(self._context.extractors)
