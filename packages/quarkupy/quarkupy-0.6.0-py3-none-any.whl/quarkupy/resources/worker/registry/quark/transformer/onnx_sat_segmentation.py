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
from ......types.worker.registry.quark.transformer import onnx_sat_segmentation_run_params

__all__ = ["OnnxSatSegmentationResource", "AsyncOnnxSatSegmentationResource"]


class OnnxSatSegmentationResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> OnnxSatSegmentationResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/quarklabsai/quarkupy#accessing-raw-response-data-eg-headers
        """
        return OnnxSatSegmentationResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> OnnxSatSegmentationResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/quarklabsai/quarkupy#with_streaming_response
        """
        return OnnxSatSegmentationResourceWithStreamingResponse(self)

    def run(
        self,
        *,
        flow_id: str,
        ipc_dataset_id: str,
        opt_input_column: str | NotGiven = NOT_GIVEN,
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
            "/worker/registry/quark/transformer/onnx_sat_segmentation/run",
            body=maybe_transform(
                {
                    "flow_id": flow_id,
                    "ipc_dataset_id": ipc_dataset_id,
                    "opt_input_column": opt_input_column,
                },
                onnx_sat_segmentation_run_params.OnnxSatSegmentationRunParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=QuarkHistoryItem,
        )


class AsyncOnnxSatSegmentationResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncOnnxSatSegmentationResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/quarklabsai/quarkupy#accessing-raw-response-data-eg-headers
        """
        return AsyncOnnxSatSegmentationResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncOnnxSatSegmentationResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/quarklabsai/quarkupy#with_streaming_response
        """
        return AsyncOnnxSatSegmentationResourceWithStreamingResponse(self)

    async def run(
        self,
        *,
        flow_id: str,
        ipc_dataset_id: str,
        opt_input_column: str | NotGiven = NOT_GIVEN,
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
            "/worker/registry/quark/transformer/onnx_sat_segmentation/run",
            body=await async_maybe_transform(
                {
                    "flow_id": flow_id,
                    "ipc_dataset_id": ipc_dataset_id,
                    "opt_input_column": opt_input_column,
                },
                onnx_sat_segmentation_run_params.OnnxSatSegmentationRunParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=QuarkHistoryItem,
        )


class OnnxSatSegmentationResourceWithRawResponse:
    def __init__(self, onnx_sat_segmentation: OnnxSatSegmentationResource) -> None:
        self._onnx_sat_segmentation = onnx_sat_segmentation

        self.run = to_raw_response_wrapper(
            onnx_sat_segmentation.run,
        )


class AsyncOnnxSatSegmentationResourceWithRawResponse:
    def __init__(self, onnx_sat_segmentation: AsyncOnnxSatSegmentationResource) -> None:
        self._onnx_sat_segmentation = onnx_sat_segmentation

        self.run = async_to_raw_response_wrapper(
            onnx_sat_segmentation.run,
        )


class OnnxSatSegmentationResourceWithStreamingResponse:
    def __init__(self, onnx_sat_segmentation: OnnxSatSegmentationResource) -> None:
        self._onnx_sat_segmentation = onnx_sat_segmentation

        self.run = to_streamed_response_wrapper(
            onnx_sat_segmentation.run,
        )


class AsyncOnnxSatSegmentationResourceWithStreamingResponse:
    def __init__(self, onnx_sat_segmentation: AsyncOnnxSatSegmentationResource) -> None:
        self._onnx_sat_segmentation = onnx_sat_segmentation

        self.run = async_to_streamed_response_wrapper(
            onnx_sat_segmentation.run,
        )
