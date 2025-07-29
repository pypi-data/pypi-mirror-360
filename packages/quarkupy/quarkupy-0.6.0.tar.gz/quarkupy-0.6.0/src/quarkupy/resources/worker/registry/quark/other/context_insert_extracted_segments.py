# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ......_types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ......_utils import maybe_transform, async_maybe_transform
from ......_compat import cached_property
from ......_resource import SyncAPIResource, AsyncAPIResource
from ......_response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ......_base_client import make_request_options
from ......types.history.quark_history_item import QuarkHistoryItem
from ......types.worker.registry.quark.other import context_insert_extracted_segment_run_params

__all__ = ["ContextInsertExtractedSegmentsResource", "AsyncContextInsertExtractedSegmentsResource"]


class ContextInsertExtractedSegmentsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ContextInsertExtractedSegmentsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/quarklabsai/quarkupy#accessing-raw-response-data-eg-headers
        """
        return ContextInsertExtractedSegmentsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ContextInsertExtractedSegmentsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/quarklabsai/quarkupy#with_streaming_response
        """
        return ContextInsertExtractedSegmentsResourceWithStreamingResponse(self)

    def run(
        self,
        *,
        flow_id: str,
        ipc_dataset_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> QuarkHistoryItem:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "application/json; charset=utf-8", **(extra_headers or {})}
        return self._post(
            "/worker/registry/quark/other/context_insert_extracted_segments/run",
            body=maybe_transform(
                {
                    "flow_id": flow_id,
                    "ipc_dataset_id": ipc_dataset_id,
                },
                context_insert_extracted_segment_run_params.ContextInsertExtractedSegmentRunParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=QuarkHistoryItem,
        )


class AsyncContextInsertExtractedSegmentsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncContextInsertExtractedSegmentsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/quarklabsai/quarkupy#accessing-raw-response-data-eg-headers
        """
        return AsyncContextInsertExtractedSegmentsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncContextInsertExtractedSegmentsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/quarklabsai/quarkupy#with_streaming_response
        """
        return AsyncContextInsertExtractedSegmentsResourceWithStreamingResponse(self)

    async def run(
        self,
        *,
        flow_id: str,
        ipc_dataset_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> QuarkHistoryItem:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "application/json; charset=utf-8", **(extra_headers or {})}
        return await self._post(
            "/worker/registry/quark/other/context_insert_extracted_segments/run",
            body=await async_maybe_transform(
                {
                    "flow_id": flow_id,
                    "ipc_dataset_id": ipc_dataset_id,
                },
                context_insert_extracted_segment_run_params.ContextInsertExtractedSegmentRunParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=QuarkHistoryItem,
        )


class ContextInsertExtractedSegmentsResourceWithRawResponse:
    def __init__(self, context_insert_extracted_segments: ContextInsertExtractedSegmentsResource) -> None:
        self._context_insert_extracted_segments = context_insert_extracted_segments

        self.run = to_raw_response_wrapper(
            context_insert_extracted_segments.run,
        )


class AsyncContextInsertExtractedSegmentsResourceWithRawResponse:
    def __init__(self, context_insert_extracted_segments: AsyncContextInsertExtractedSegmentsResource) -> None:
        self._context_insert_extracted_segments = context_insert_extracted_segments

        self.run = async_to_raw_response_wrapper(
            context_insert_extracted_segments.run,
        )


class ContextInsertExtractedSegmentsResourceWithStreamingResponse:
    def __init__(self, context_insert_extracted_segments: ContextInsertExtractedSegmentsResource) -> None:
        self._context_insert_extracted_segments = context_insert_extracted_segments

        self.run = to_streamed_response_wrapper(
            context_insert_extracted_segments.run,
        )


class AsyncContextInsertExtractedSegmentsResourceWithStreamingResponse:
    def __init__(self, context_insert_extracted_segments: AsyncContextInsertExtractedSegmentsResource) -> None:
        self._context_insert_extracted_segments = context_insert_extracted_segments

        self.run = async_to_streamed_response_wrapper(
            context_insert_extracted_segments.run,
        )
