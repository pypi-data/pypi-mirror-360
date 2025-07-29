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
from ......types.worker.registry.quark.vector import lancedb_search_run_params

__all__ = ["LancedbSearchResource", "AsyncLancedbSearchResource"]


class LancedbSearchResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> LancedbSearchResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/quarklabsai/quarkupy#accessing-raw-response-data-eg-headers
        """
        return LancedbSearchResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> LancedbSearchResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/quarklabsai/quarkupy#with_streaming_response
        """
        return LancedbSearchResourceWithStreamingResponse(self)

    def run(
        self,
        *,
        lattice_id: str,
        query: lancedb_search_run_params.Query,
        table_name: str,
        opt_uri: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> QuarkHistoryItem:
        """
        Args:
          query: Represents the simple input a Quark/Lattice - usually used for inference

              TODO: Replace this with
              [Issue 23](https://github.com/ProjectBifrost/bifrost/issues/23)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "application/json; charset=utf-8", **(extra_headers or {})}
        return self._post(
            "/worker/registry/quark/vector/lancedb_search/run",
            body=maybe_transform(
                {
                    "lattice_id": lattice_id,
                    "query": query,
                    "table_name": table_name,
                    "opt_uri": opt_uri,
                },
                lancedb_search_run_params.LancedbSearchRunParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=QuarkHistoryItem,
        )


class AsyncLancedbSearchResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncLancedbSearchResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/quarklabsai/quarkupy#accessing-raw-response-data-eg-headers
        """
        return AsyncLancedbSearchResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncLancedbSearchResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/quarklabsai/quarkupy#with_streaming_response
        """
        return AsyncLancedbSearchResourceWithStreamingResponse(self)

    async def run(
        self,
        *,
        lattice_id: str,
        query: lancedb_search_run_params.Query,
        table_name: str,
        opt_uri: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> QuarkHistoryItem:
        """
        Args:
          query: Represents the simple input a Quark/Lattice - usually used for inference

              TODO: Replace this with
              [Issue 23](https://github.com/ProjectBifrost/bifrost/issues/23)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "application/json; charset=utf-8", **(extra_headers or {})}
        return await self._post(
            "/worker/registry/quark/vector/lancedb_search/run",
            body=await async_maybe_transform(
                {
                    "lattice_id": lattice_id,
                    "query": query,
                    "table_name": table_name,
                    "opt_uri": opt_uri,
                },
                lancedb_search_run_params.LancedbSearchRunParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=QuarkHistoryItem,
        )


class LancedbSearchResourceWithRawResponse:
    def __init__(self, lancedb_search: LancedbSearchResource) -> None:
        self._lancedb_search = lancedb_search

        self.run = to_raw_response_wrapper(
            lancedb_search.run,
        )


class AsyncLancedbSearchResourceWithRawResponse:
    def __init__(self, lancedb_search: AsyncLancedbSearchResource) -> None:
        self._lancedb_search = lancedb_search

        self.run = async_to_raw_response_wrapper(
            lancedb_search.run,
        )


class LancedbSearchResourceWithStreamingResponse:
    def __init__(self, lancedb_search: LancedbSearchResource) -> None:
        self._lancedb_search = lancedb_search

        self.run = to_streamed_response_wrapper(
            lancedb_search.run,
        )


class AsyncLancedbSearchResourceWithStreamingResponse:
    def __init__(self, lancedb_search: AsyncLancedbSearchResource) -> None:
        self._lancedb_search = lancedb_search

        self.run = async_to_streamed_response_wrapper(
            lancedb_search.run,
        )
