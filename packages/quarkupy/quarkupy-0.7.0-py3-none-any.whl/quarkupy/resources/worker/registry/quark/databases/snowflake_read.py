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
from ......types.worker.registry.quark.databases import snowflake_read_run_params

__all__ = ["SnowflakeReadResource", "AsyncSnowflakeReadResource"]


class SnowflakeReadResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> SnowflakeReadResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/quarklabsai/quarkupy#accessing-raw-response-data-eg-headers
        """
        return SnowflakeReadResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> SnowflakeReadResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/quarklabsai/quarkupy#with_streaming_response
        """
        return SnowflakeReadResourceWithStreamingResponse(self)

    def run(
        self,
        *,
        account: str,
        auth: snowflake_read_run_params.Auth,
        lattice_id: str,
        query: str,
        opt_database: str | NotGiven = NOT_GIVEN,
        opt_role: str | NotGiven = NOT_GIVEN,
        opt_schema: str | NotGiven = NOT_GIVEN,
        opt_warehouse: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> QuarkHistoryItem:
        """
        Args:
          account: Snowflake Account ID

          auth: Authentication Details

          opt_database: Snowflake Database

          opt_role: Executing Role

          opt_schema: Snowflake Schema

          opt_warehouse: Snowflake Warehouse

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "application/json; charset=utf-8", **(extra_headers or {})}
        return self._post(
            "/worker/registry/quark/databases/snowflake_read/run",
            body=maybe_transform(
                {
                    "account": account,
                    "auth": auth,
                    "lattice_id": lattice_id,
                    "query": query,
                    "opt_database": opt_database,
                    "opt_role": opt_role,
                    "opt_schema": opt_schema,
                    "opt_warehouse": opt_warehouse,
                },
                snowflake_read_run_params.SnowflakeReadRunParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=QuarkHistoryItem,
        )


class AsyncSnowflakeReadResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncSnowflakeReadResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/quarklabsai/quarkupy#accessing-raw-response-data-eg-headers
        """
        return AsyncSnowflakeReadResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncSnowflakeReadResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/quarklabsai/quarkupy#with_streaming_response
        """
        return AsyncSnowflakeReadResourceWithStreamingResponse(self)

    async def run(
        self,
        *,
        account: str,
        auth: snowflake_read_run_params.Auth,
        lattice_id: str,
        query: str,
        opt_database: str | NotGiven = NOT_GIVEN,
        opt_role: str | NotGiven = NOT_GIVEN,
        opt_schema: str | NotGiven = NOT_GIVEN,
        opt_warehouse: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> QuarkHistoryItem:
        """
        Args:
          account: Snowflake Account ID

          auth: Authentication Details

          opt_database: Snowflake Database

          opt_role: Executing Role

          opt_schema: Snowflake Schema

          opt_warehouse: Snowflake Warehouse

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "application/json; charset=utf-8", **(extra_headers or {})}
        return await self._post(
            "/worker/registry/quark/databases/snowflake_read/run",
            body=await async_maybe_transform(
                {
                    "account": account,
                    "auth": auth,
                    "lattice_id": lattice_id,
                    "query": query,
                    "opt_database": opt_database,
                    "opt_role": opt_role,
                    "opt_schema": opt_schema,
                    "opt_warehouse": opt_warehouse,
                },
                snowflake_read_run_params.SnowflakeReadRunParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=QuarkHistoryItem,
        )


class SnowflakeReadResourceWithRawResponse:
    def __init__(self, snowflake_read: SnowflakeReadResource) -> None:
        self._snowflake_read = snowflake_read

        self.run = to_raw_response_wrapper(
            snowflake_read.run,
        )


class AsyncSnowflakeReadResourceWithRawResponse:
    def __init__(self, snowflake_read: AsyncSnowflakeReadResource) -> None:
        self._snowflake_read = snowflake_read

        self.run = async_to_raw_response_wrapper(
            snowflake_read.run,
        )


class SnowflakeReadResourceWithStreamingResponse:
    def __init__(self, snowflake_read: SnowflakeReadResource) -> None:
        self._snowflake_read = snowflake_read

        self.run = to_streamed_response_wrapper(
            snowflake_read.run,
        )


class AsyncSnowflakeReadResourceWithStreamingResponse:
    def __init__(self, snowflake_read: AsyncSnowflakeReadResource) -> None:
        self._snowflake_read = snowflake_read

        self.run = async_to_streamed_response_wrapper(
            snowflake_read.run,
        )
