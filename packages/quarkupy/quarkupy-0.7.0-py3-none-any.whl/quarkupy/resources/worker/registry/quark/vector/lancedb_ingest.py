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
from ......types.worker.registry.quark.vector import lancedb_ingest_run_params

__all__ = ["LancedbIngestResource", "AsyncLancedbIngestResource"]


class LancedbIngestResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> LancedbIngestResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/quarklabsai/quarkupy#accessing-raw-response-data-eg-headers
        """
        return LancedbIngestResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> LancedbIngestResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/quarklabsai/quarkupy#with_streaming_response
        """
        return LancedbIngestResourceWithStreamingResponse(self)

    def run(
        self,
        *,
        ipc_dataset_id: str,
        lattice_id: str,
        table_name: str,
        opt_operation: str | NotGiven = NOT_GIVEN,
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
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "application/json; charset=utf-8", **(extra_headers or {})}
        return self._post(
            "/worker/registry/quark/vector/lancedb_ingest/run",
            body=maybe_transform(
                {
                    "ipc_dataset_id": ipc_dataset_id,
                    "lattice_id": lattice_id,
                    "table_name": table_name,
                    "opt_operation": opt_operation,
                    "opt_uri": opt_uri,
                },
                lancedb_ingest_run_params.LancedbIngestRunParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=QuarkHistoryItem,
        )


class AsyncLancedbIngestResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncLancedbIngestResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/quarklabsai/quarkupy#accessing-raw-response-data-eg-headers
        """
        return AsyncLancedbIngestResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncLancedbIngestResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/quarklabsai/quarkupy#with_streaming_response
        """
        return AsyncLancedbIngestResourceWithStreamingResponse(self)

    async def run(
        self,
        *,
        ipc_dataset_id: str,
        lattice_id: str,
        table_name: str,
        opt_operation: str | NotGiven = NOT_GIVEN,
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
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "application/json; charset=utf-8", **(extra_headers or {})}
        return await self._post(
            "/worker/registry/quark/vector/lancedb_ingest/run",
            body=await async_maybe_transform(
                {
                    "ipc_dataset_id": ipc_dataset_id,
                    "lattice_id": lattice_id,
                    "table_name": table_name,
                    "opt_operation": opt_operation,
                    "opt_uri": opt_uri,
                },
                lancedb_ingest_run_params.LancedbIngestRunParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=QuarkHistoryItem,
        )


class LancedbIngestResourceWithRawResponse:
    def __init__(self, lancedb_ingest: LancedbIngestResource) -> None:
        self._lancedb_ingest = lancedb_ingest

        self.run = to_raw_response_wrapper(
            lancedb_ingest.run,
        )


class AsyncLancedbIngestResourceWithRawResponse:
    def __init__(self, lancedb_ingest: AsyncLancedbIngestResource) -> None:
        self._lancedb_ingest = lancedb_ingest

        self.run = async_to_raw_response_wrapper(
            lancedb_ingest.run,
        )


class LancedbIngestResourceWithStreamingResponse:
    def __init__(self, lancedb_ingest: LancedbIngestResource) -> None:
        self._lancedb_ingest = lancedb_ingest

        self.run = to_streamed_response_wrapper(
            lancedb_ingest.run,
        )


class AsyncLancedbIngestResourceWithStreamingResponse:
    def __init__(self, lancedb_ingest: AsyncLancedbIngestResource) -> None:
        self._lancedb_ingest = lancedb_ingest

        self.run = async_to_streamed_response_wrapper(
            lancedb_ingest.run,
        )
