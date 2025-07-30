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
from ......types.worker.registry.quark.other import context_insert_segment_run_params

__all__ = ["ContextInsertSegmentsResource", "AsyncContextInsertSegmentsResource"]


class ContextInsertSegmentsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ContextInsertSegmentsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/quarklabsai/quarkupy#accessing-raw-response-data-eg-headers
        """
        return ContextInsertSegmentsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ContextInsertSegmentsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/quarklabsai/quarkupy#with_streaming_response
        """
        return ContextInsertSegmentsResourceWithStreamingResponse(self)

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
            "/worker/registry/quark/other/context_insert_segments/run",
            body=maybe_transform(
                {
                    "flow_id": flow_id,
                    "ipc_dataset_id": ipc_dataset_id,
                },
                context_insert_segment_run_params.ContextInsertSegmentRunParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=QuarkHistoryItem,
        )


class AsyncContextInsertSegmentsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncContextInsertSegmentsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/quarklabsai/quarkupy#accessing-raw-response-data-eg-headers
        """
        return AsyncContextInsertSegmentsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncContextInsertSegmentsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/quarklabsai/quarkupy#with_streaming_response
        """
        return AsyncContextInsertSegmentsResourceWithStreamingResponse(self)

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
            "/worker/registry/quark/other/context_insert_segments/run",
            body=await async_maybe_transform(
                {
                    "flow_id": flow_id,
                    "ipc_dataset_id": ipc_dataset_id,
                },
                context_insert_segment_run_params.ContextInsertSegmentRunParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=QuarkHistoryItem,
        )


class ContextInsertSegmentsResourceWithRawResponse:
    def __init__(self, context_insert_segments: ContextInsertSegmentsResource) -> None:
        self._context_insert_segments = context_insert_segments

        self.run = to_raw_response_wrapper(
            context_insert_segments.run,
        )


class AsyncContextInsertSegmentsResourceWithRawResponse:
    def __init__(self, context_insert_segments: AsyncContextInsertSegmentsResource) -> None:
        self._context_insert_segments = context_insert_segments

        self.run = async_to_raw_response_wrapper(
            context_insert_segments.run,
        )


class ContextInsertSegmentsResourceWithStreamingResponse:
    def __init__(self, context_insert_segments: ContextInsertSegmentsResource) -> None:
        self._context_insert_segments = context_insert_segments

        self.run = to_streamed_response_wrapper(
            context_insert_segments.run,
        )


class AsyncContextInsertSegmentsResourceWithStreamingResponse:
    def __init__(self, context_insert_segments: AsyncContextInsertSegmentsResource) -> None:
        self._context_insert_segments = context_insert_segments

        self.run = async_to_streamed_response_wrapper(
            context_insert_segments.run,
        )
