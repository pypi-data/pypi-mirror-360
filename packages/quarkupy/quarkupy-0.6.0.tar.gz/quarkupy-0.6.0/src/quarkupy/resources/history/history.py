# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from datetime import datetime

import httpx

from .flow import (
    FlowResource,
    AsyncFlowResource,
    FlowResourceWithRawResponse,
    AsyncFlowResourceWithRawResponse,
    FlowResourceWithStreamingResponse,
    AsyncFlowResourceWithStreamingResponse,
)
from .quark import (
    QuarkResource,
    AsyncQuarkResource,
    QuarkResourceWithRawResponse,
    AsyncQuarkResourceWithRawResponse,
    QuarkResourceWithStreamingResponse,
    AsyncQuarkResourceWithStreamingResponse,
)
from ...types import history_list_flows_params, history_list_quarks_params
from ..._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ..._utils import maybe_transform, async_maybe_transform
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ..._base_client import make_request_options
from ...types.history_list_response import HistoryListResponse
from ...types.history_list_flows_response import HistoryListFlowsResponse
from ...types.history_list_quarks_response import HistoryListQuarksResponse
from ...types.context.success_response_message import SuccessResponseMessage

__all__ = ["HistoryResource", "AsyncHistoryResource"]


class HistoryResource(SyncAPIResource):
    @cached_property
    def quark(self) -> QuarkResource:
        return QuarkResource(self._client)

    @cached_property
    def flow(self) -> FlowResource:
        return FlowResource(self._client)

    @cached_property
    def with_raw_response(self) -> HistoryResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/quarklabsai/quarkupy#accessing-raw-response-data-eg-headers
        """
        return HistoryResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> HistoryResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/quarklabsai/quarkupy#with_streaming_response
        """
        return HistoryResourceWithStreamingResponse(self)

    def list(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> HistoryListResponse:
        extra_headers = {"Accept": "application/json; charset=utf-8", **(extra_headers or {})}
        return self._get(
            "/history",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=HistoryListResponse,
        )

    def clear_all(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SuccessResponseMessage:
        extra_headers = {"Accept": "application/json; charset=utf-8", **(extra_headers or {})}
        return self._get(
            "/history/clear_all_history",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SuccessResponseMessage,
        )

    def list_flows(
        self,
        *,
        max_timestamp: Union[str, datetime] | NotGiven = NOT_GIVEN,
        min_timestamp: Union[str, datetime] | NotGiven = NOT_GIVEN,
        registry_identifier: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> HistoryListFlowsResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "application/json; charset=utf-8", **(extra_headers or {})}
        return self._get(
            "/history/flows",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "max_timestamp": max_timestamp,
                        "min_timestamp": min_timestamp,
                        "registry_identifier": registry_identifier,
                    },
                    history_list_flows_params.HistoryListFlowsParams,
                ),
            ),
            cast_to=HistoryListFlowsResponse,
        )

    def list_quarks(
        self,
        *,
        lattice_id: str | NotGiven = NOT_GIVEN,
        max_timestamp: Union[str, datetime] | NotGiven = NOT_GIVEN,
        min_timestamp: Union[str, datetime] | NotGiven = NOT_GIVEN,
        registry_identifier: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> HistoryListQuarksResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "application/json; charset=utf-8", **(extra_headers or {})}
        return self._get(
            "/history/quarks",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "lattice_id": lattice_id,
                        "max_timestamp": max_timestamp,
                        "min_timestamp": min_timestamp,
                        "registry_identifier": registry_identifier,
                    },
                    history_list_quarks_params.HistoryListQuarksParams,
                ),
            ),
            cast_to=HistoryListQuarksResponse,
        )


class AsyncHistoryResource(AsyncAPIResource):
    @cached_property
    def quark(self) -> AsyncQuarkResource:
        return AsyncQuarkResource(self._client)

    @cached_property
    def flow(self) -> AsyncFlowResource:
        return AsyncFlowResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncHistoryResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/quarklabsai/quarkupy#accessing-raw-response-data-eg-headers
        """
        return AsyncHistoryResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncHistoryResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/quarklabsai/quarkupy#with_streaming_response
        """
        return AsyncHistoryResourceWithStreamingResponse(self)

    async def list(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> HistoryListResponse:
        extra_headers = {"Accept": "application/json; charset=utf-8", **(extra_headers or {})}
        return await self._get(
            "/history",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=HistoryListResponse,
        )

    async def clear_all(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SuccessResponseMessage:
        extra_headers = {"Accept": "application/json; charset=utf-8", **(extra_headers or {})}
        return await self._get(
            "/history/clear_all_history",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SuccessResponseMessage,
        )

    async def list_flows(
        self,
        *,
        max_timestamp: Union[str, datetime] | NotGiven = NOT_GIVEN,
        min_timestamp: Union[str, datetime] | NotGiven = NOT_GIVEN,
        registry_identifier: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> HistoryListFlowsResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "application/json; charset=utf-8", **(extra_headers or {})}
        return await self._get(
            "/history/flows",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "max_timestamp": max_timestamp,
                        "min_timestamp": min_timestamp,
                        "registry_identifier": registry_identifier,
                    },
                    history_list_flows_params.HistoryListFlowsParams,
                ),
            ),
            cast_to=HistoryListFlowsResponse,
        )

    async def list_quarks(
        self,
        *,
        lattice_id: str | NotGiven = NOT_GIVEN,
        max_timestamp: Union[str, datetime] | NotGiven = NOT_GIVEN,
        min_timestamp: Union[str, datetime] | NotGiven = NOT_GIVEN,
        registry_identifier: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> HistoryListQuarksResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "application/json; charset=utf-8", **(extra_headers or {})}
        return await self._get(
            "/history/quarks",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "lattice_id": lattice_id,
                        "max_timestamp": max_timestamp,
                        "min_timestamp": min_timestamp,
                        "registry_identifier": registry_identifier,
                    },
                    history_list_quarks_params.HistoryListQuarksParams,
                ),
            ),
            cast_to=HistoryListQuarksResponse,
        )


class HistoryResourceWithRawResponse:
    def __init__(self, history: HistoryResource) -> None:
        self._history = history

        self.list = to_raw_response_wrapper(
            history.list,
        )
        self.clear_all = to_raw_response_wrapper(
            history.clear_all,
        )
        self.list_flows = to_raw_response_wrapper(
            history.list_flows,
        )
        self.list_quarks = to_raw_response_wrapper(
            history.list_quarks,
        )

    @cached_property
    def quark(self) -> QuarkResourceWithRawResponse:
        return QuarkResourceWithRawResponse(self._history.quark)

    @cached_property
    def flow(self) -> FlowResourceWithRawResponse:
        return FlowResourceWithRawResponse(self._history.flow)


class AsyncHistoryResourceWithRawResponse:
    def __init__(self, history: AsyncHistoryResource) -> None:
        self._history = history

        self.list = async_to_raw_response_wrapper(
            history.list,
        )
        self.clear_all = async_to_raw_response_wrapper(
            history.clear_all,
        )
        self.list_flows = async_to_raw_response_wrapper(
            history.list_flows,
        )
        self.list_quarks = async_to_raw_response_wrapper(
            history.list_quarks,
        )

    @cached_property
    def quark(self) -> AsyncQuarkResourceWithRawResponse:
        return AsyncQuarkResourceWithRawResponse(self._history.quark)

    @cached_property
    def flow(self) -> AsyncFlowResourceWithRawResponse:
        return AsyncFlowResourceWithRawResponse(self._history.flow)


class HistoryResourceWithStreamingResponse:
    def __init__(self, history: HistoryResource) -> None:
        self._history = history

        self.list = to_streamed_response_wrapper(
            history.list,
        )
        self.clear_all = to_streamed_response_wrapper(
            history.clear_all,
        )
        self.list_flows = to_streamed_response_wrapper(
            history.list_flows,
        )
        self.list_quarks = to_streamed_response_wrapper(
            history.list_quarks,
        )

    @cached_property
    def quark(self) -> QuarkResourceWithStreamingResponse:
        return QuarkResourceWithStreamingResponse(self._history.quark)

    @cached_property
    def flow(self) -> FlowResourceWithStreamingResponse:
        return FlowResourceWithStreamingResponse(self._history.flow)


class AsyncHistoryResourceWithStreamingResponse:
    def __init__(self, history: AsyncHistoryResource) -> None:
        self._history = history

        self.list = async_to_streamed_response_wrapper(
            history.list,
        )
        self.clear_all = async_to_streamed_response_wrapper(
            history.clear_all,
        )
        self.list_flows = async_to_streamed_response_wrapper(
            history.list_flows,
        )
        self.list_quarks = async_to_streamed_response_wrapper(
            history.list_quarks,
        )

    @cached_property
    def quark(self) -> AsyncQuarkResourceWithStreamingResponse:
        return AsyncQuarkResourceWithStreamingResponse(self._history.quark)

    @cached_property
    def flow(self) -> AsyncFlowResourceWithStreamingResponse:
        return AsyncFlowResourceWithStreamingResponse(self._history.flow)
