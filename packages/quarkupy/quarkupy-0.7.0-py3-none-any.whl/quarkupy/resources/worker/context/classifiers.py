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
from ....types.worker.context import classifier_list_params

__all__ = ["ClassifiersResource", "AsyncClassifiersResource"]


class ClassifiersResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ClassifiersResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/quarklabsai/quarkupy#accessing-raw-response-data-eg-headers
        """
        return ClassifiersResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ClassifiersResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/quarklabsai/quarkupy#with_streaming_response
        """
        return ClassifiersResourceWithStreamingResponse(self)

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
            "/worker/context/classifiers",
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
                    classifier_list_params.ClassifierListParams,
                ),
            ),
            cast_to=BinaryAPIResponse,
        )

    def retrieve_text(
        self,
        classifier_id: str,
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
        if not classifier_id:
            raise ValueError(f"Expected a non-empty value for `classifier_id` but received {classifier_id!r}")
        extra_headers = {"Accept": "application/x-apache-arrow-stream", **(extra_headers or {})}
        return self._get(
            f"/worker/context/classifiers/{classifier_id}/text",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BinaryAPIResponse,
        )


class AsyncClassifiersResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncClassifiersResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/quarklabsai/quarkupy#accessing-raw-response-data-eg-headers
        """
        return AsyncClassifiersResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncClassifiersResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/quarklabsai/quarkupy#with_streaming_response
        """
        return AsyncClassifiersResourceWithStreamingResponse(self)

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
            "/worker/context/classifiers",
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
                    classifier_list_params.ClassifierListParams,
                ),
            ),
            cast_to=AsyncBinaryAPIResponse,
        )

    async def retrieve_text(
        self,
        classifier_id: str,
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
        if not classifier_id:
            raise ValueError(f"Expected a non-empty value for `classifier_id` but received {classifier_id!r}")
        extra_headers = {"Accept": "application/x-apache-arrow-stream", **(extra_headers or {})}
        return await self._get(
            f"/worker/context/classifiers/{classifier_id}/text",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AsyncBinaryAPIResponse,
        )


class ClassifiersResourceWithRawResponse:
    def __init__(self, classifiers: ClassifiersResource) -> None:
        self._classifiers = classifiers

        self.list = to_custom_raw_response_wrapper(
            classifiers.list,
            BinaryAPIResponse,
        )
        self.retrieve_text = to_custom_raw_response_wrapper(
            classifiers.retrieve_text,
            BinaryAPIResponse,
        )


class AsyncClassifiersResourceWithRawResponse:
    def __init__(self, classifiers: AsyncClassifiersResource) -> None:
        self._classifiers = classifiers

        self.list = async_to_custom_raw_response_wrapper(
            classifiers.list,
            AsyncBinaryAPIResponse,
        )
        self.retrieve_text = async_to_custom_raw_response_wrapper(
            classifiers.retrieve_text,
            AsyncBinaryAPIResponse,
        )


class ClassifiersResourceWithStreamingResponse:
    def __init__(self, classifiers: ClassifiersResource) -> None:
        self._classifiers = classifiers

        self.list = to_custom_streamed_response_wrapper(
            classifiers.list,
            StreamedBinaryAPIResponse,
        )
        self.retrieve_text = to_custom_streamed_response_wrapper(
            classifiers.retrieve_text,
            StreamedBinaryAPIResponse,
        )


class AsyncClassifiersResourceWithStreamingResponse:
    def __init__(self, classifiers: AsyncClassifiersResource) -> None:
        self._classifiers = classifiers

        self.list = async_to_custom_streamed_response_wrapper(
            classifiers.list,
            AsyncStreamedBinaryAPIResponse,
        )
        self.retrieve_text = async_to_custom_streamed_response_wrapper(
            classifiers.retrieve_text,
            AsyncStreamedBinaryAPIResponse,
        )
