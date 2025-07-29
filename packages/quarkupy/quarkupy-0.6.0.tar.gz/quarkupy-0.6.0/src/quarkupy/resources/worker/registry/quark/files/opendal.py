# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List

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
from ......types.worker.registry.quark.files import QuarkFileObjectStatus, opendal_run_params
from ......types.worker.registry.quark.files.quark_file_object_status import QuarkFileObjectStatus

__all__ = ["OpendalResource", "AsyncOpendalResource"]


class OpendalResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> OpendalResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/quarklabsai/quarkupy#accessing-raw-response-data-eg-headers
        """
        return OpendalResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> OpendalResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/quarklabsai/quarkupy#with_streaming_response
        """
        return OpendalResourceWithStreamingResponse(self)

    def run(
        self,
        *,
        config: opendal_run_params.Config,
        flow_id: str,
        source_id: str,
        opt_paths: List[str] | NotGiven = NOT_GIVEN,
        opt_recursive: bool | NotGiven = NOT_GIVEN,
        opt_set_status: QuarkFileObjectStatus | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> QuarkHistoryItem:
        """
        Args:
          config: OpenAPI compatible set of configs

          opt_paths: Filter read by paths (directories or files)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "application/json; charset=utf-8", **(extra_headers or {})}
        return self._post(
            "/worker/registry/quark/files/opendal/run",
            body=maybe_transform(
                {
                    "config": config,
                    "flow_id": flow_id,
                    "source_id": source_id,
                    "opt_paths": opt_paths,
                    "opt_recursive": opt_recursive,
                    "opt_set_status": opt_set_status,
                },
                opendal_run_params.OpendalRunParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=QuarkHistoryItem,
        )

    def schema(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        extra_headers = {"Accept": "application/json; charset=utf-8", **(extra_headers or {})}
        return self._post(
            "/worker/registry/quark/files/opendal/schema",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )


class AsyncOpendalResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncOpendalResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/quarklabsai/quarkupy#accessing-raw-response-data-eg-headers
        """
        return AsyncOpendalResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncOpendalResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/quarklabsai/quarkupy#with_streaming_response
        """
        return AsyncOpendalResourceWithStreamingResponse(self)

    async def run(
        self,
        *,
        config: opendal_run_params.Config,
        flow_id: str,
        source_id: str,
        opt_paths: List[str] | NotGiven = NOT_GIVEN,
        opt_recursive: bool | NotGiven = NOT_GIVEN,
        opt_set_status: QuarkFileObjectStatus | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> QuarkHistoryItem:
        """
        Args:
          config: OpenAPI compatible set of configs

          opt_paths: Filter read by paths (directories or files)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "application/json; charset=utf-8", **(extra_headers or {})}
        return await self._post(
            "/worker/registry/quark/files/opendal/run",
            body=await async_maybe_transform(
                {
                    "config": config,
                    "flow_id": flow_id,
                    "source_id": source_id,
                    "opt_paths": opt_paths,
                    "opt_recursive": opt_recursive,
                    "opt_set_status": opt_set_status,
                },
                opendal_run_params.OpendalRunParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=QuarkHistoryItem,
        )

    async def schema(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        extra_headers = {"Accept": "application/json; charset=utf-8", **(extra_headers or {})}
        return await self._post(
            "/worker/registry/quark/files/opendal/schema",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )


class OpendalResourceWithRawResponse:
    def __init__(self, opendal: OpendalResource) -> None:
        self._opendal = opendal

        self.run = to_raw_response_wrapper(
            opendal.run,
        )
        self.schema = to_raw_response_wrapper(
            opendal.schema,
        )


class AsyncOpendalResourceWithRawResponse:
    def __init__(self, opendal: AsyncOpendalResource) -> None:
        self._opendal = opendal

        self.run = async_to_raw_response_wrapper(
            opendal.run,
        )
        self.schema = async_to_raw_response_wrapper(
            opendal.schema,
        )


class OpendalResourceWithStreamingResponse:
    def __init__(self, opendal: OpendalResource) -> None:
        self._opendal = opendal

        self.run = to_streamed_response_wrapper(
            opendal.run,
        )
        self.schema = to_streamed_response_wrapper(
            opendal.schema,
        )


class AsyncOpendalResourceWithStreamingResponse:
    def __init__(self, opendal: AsyncOpendalResource) -> None:
        self._opendal = opendal

        self.run = async_to_streamed_response_wrapper(
            opendal.run,
        )
        self.schema = async_to_streamed_response_wrapper(
            opendal.schema,
        )
