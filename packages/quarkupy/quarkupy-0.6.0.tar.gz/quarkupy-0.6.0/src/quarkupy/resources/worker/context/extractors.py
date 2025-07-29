# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ...._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ...._utils import maybe_transform, async_maybe_transform
from ...._compat import cached_property
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
from ....types.worker.context import extractor_list_params

__all__ = ["ExtractorsResource", "AsyncExtractorsResource"]


class ExtractorsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ExtractorsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/quarklabsai/quarkupy#accessing-raw-response-data-eg-headers
        """
        return ExtractorsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ExtractorsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/quarklabsai/quarkupy#with_streaming_response
        """
        return ExtractorsResourceWithStreamingResponse(self)

    def list(
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
            "/worker/context/extractors",
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
                    extractor_list_params.ExtractorListParams,
                ),
            ),
            cast_to=BinaryAPIResponse,
        )

    def retrieve_text(
        self,
        extractor_id: str,
        *,
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
        if not extractor_id:
            raise ValueError(f"Expected a non-empty value for `extractor_id` but received {extractor_id!r}")
        extra_headers = {"Accept": "application/x-apache-arrow-stream", **(extra_headers or {})}
        return self._get(
            f"/worker/context/extractors/{extractor_id}/text",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BinaryAPIResponse,
        )


class AsyncExtractorsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncExtractorsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/quarklabsai/quarkupy#accessing-raw-response-data-eg-headers
        """
        return AsyncExtractorsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncExtractorsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/quarklabsai/quarkupy#with_streaming_response
        """
        return AsyncExtractorsResourceWithStreamingResponse(self)

    async def list(
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
            "/worker/context/extractors",
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
                    extractor_list_params.ExtractorListParams,
                ),
            ),
            cast_to=AsyncBinaryAPIResponse,
        )

    async def retrieve_text(
        self,
        extractor_id: str,
        *,
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
        if not extractor_id:
            raise ValueError(f"Expected a non-empty value for `extractor_id` but received {extractor_id!r}")
        extra_headers = {"Accept": "application/x-apache-arrow-stream", **(extra_headers or {})}
        return await self._get(
            f"/worker/context/extractors/{extractor_id}/text",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AsyncBinaryAPIResponse,
        )


class ExtractorsResourceWithRawResponse:
    def __init__(self, extractors: ExtractorsResource) -> None:
        self._extractors = extractors

        self.list = to_custom_raw_response_wrapper(
            extractors.list,
            BinaryAPIResponse,
        )
        self.retrieve_text = to_custom_raw_response_wrapper(
            extractors.retrieve_text,
            BinaryAPIResponse,
        )


class AsyncExtractorsResourceWithRawResponse:
    def __init__(self, extractors: AsyncExtractorsResource) -> None:
        self._extractors = extractors

        self.list = async_to_custom_raw_response_wrapper(
            extractors.list,
            AsyncBinaryAPIResponse,
        )
        self.retrieve_text = async_to_custom_raw_response_wrapper(
            extractors.retrieve_text,
            AsyncBinaryAPIResponse,
        )


class ExtractorsResourceWithStreamingResponse:
    def __init__(self, extractors: ExtractorsResource) -> None:
        self._extractors = extractors

        self.list = to_custom_streamed_response_wrapper(
            extractors.list,
            StreamedBinaryAPIResponse,
        )
        self.retrieve_text = to_custom_streamed_response_wrapper(
            extractors.retrieve_text,
            StreamedBinaryAPIResponse,
        )


class AsyncExtractorsResourceWithStreamingResponse:
    def __init__(self, extractors: AsyncExtractorsResource) -> None:
        self._extractors = extractors

        self.list = async_to_custom_streamed_response_wrapper(
            extractors.list,
            AsyncStreamedBinaryAPIResponse,
        )
        self.retrieve_text = async_to_custom_streamed_response_wrapper(
            extractors.retrieve_text,
            AsyncStreamedBinaryAPIResponse,
        )
