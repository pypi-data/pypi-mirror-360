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
from ......types.worker.registry.quark.transformer import docling_chunker_run_params

__all__ = ["DoclingChunkerResource", "AsyncDoclingChunkerResource"]


class DoclingChunkerResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> DoclingChunkerResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/quarklabsai/quarkupy#accessing-raw-response-data-eg-headers
        """
        return DoclingChunkerResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> DoclingChunkerResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/quarklabsai/quarkupy#with_streaming_response
        """
        return DoclingChunkerResourceWithStreamingResponse(self)

    def run(
        self,
        *,
        ipc_dataset_id: str,
        lattice_id: str,
        opt_drop_cols: List[str] | NotGiven = NOT_GIVEN,
        opt_max_tokens: int | NotGiven = NOT_GIVEN,
        opt_merge_peers: bool | NotGiven = NOT_GIVEN,
        opt_model: str | NotGiven = NOT_GIVEN,
        opt_text_col: str | NotGiven = NOT_GIVEN,
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
            "/worker/registry/quark/transformer/docling_chunker/run",
            body=maybe_transform(
                {
                    "ipc_dataset_id": ipc_dataset_id,
                    "lattice_id": lattice_id,
                    "opt_drop_cols": opt_drop_cols,
                    "opt_max_tokens": opt_max_tokens,
                    "opt_merge_peers": opt_merge_peers,
                    "opt_model": opt_model,
                    "opt_text_col": opt_text_col,
                },
                docling_chunker_run_params.DoclingChunkerRunParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=QuarkHistoryItem,
        )


class AsyncDoclingChunkerResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncDoclingChunkerResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/quarklabsai/quarkupy#accessing-raw-response-data-eg-headers
        """
        return AsyncDoclingChunkerResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncDoclingChunkerResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/quarklabsai/quarkupy#with_streaming_response
        """
        return AsyncDoclingChunkerResourceWithStreamingResponse(self)

    async def run(
        self,
        *,
        ipc_dataset_id: str,
        lattice_id: str,
        opt_drop_cols: List[str] | NotGiven = NOT_GIVEN,
        opt_max_tokens: int | NotGiven = NOT_GIVEN,
        opt_merge_peers: bool | NotGiven = NOT_GIVEN,
        opt_model: str | NotGiven = NOT_GIVEN,
        opt_text_col: str | NotGiven = NOT_GIVEN,
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
            "/worker/registry/quark/transformer/docling_chunker/run",
            body=await async_maybe_transform(
                {
                    "ipc_dataset_id": ipc_dataset_id,
                    "lattice_id": lattice_id,
                    "opt_drop_cols": opt_drop_cols,
                    "opt_max_tokens": opt_max_tokens,
                    "opt_merge_peers": opt_merge_peers,
                    "opt_model": opt_model,
                    "opt_text_col": opt_text_col,
                },
                docling_chunker_run_params.DoclingChunkerRunParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=QuarkHistoryItem,
        )


class DoclingChunkerResourceWithRawResponse:
    def __init__(self, docling_chunker: DoclingChunkerResource) -> None:
        self._docling_chunker = docling_chunker

        self.run = to_raw_response_wrapper(
            docling_chunker.run,
        )


class AsyncDoclingChunkerResourceWithRawResponse:
    def __init__(self, docling_chunker: AsyncDoclingChunkerResource) -> None:
        self._docling_chunker = docling_chunker

        self.run = async_to_raw_response_wrapper(
            docling_chunker.run,
        )


class DoclingChunkerResourceWithStreamingResponse:
    def __init__(self, docling_chunker: DoclingChunkerResource) -> None:
        self._docling_chunker = docling_chunker

        self.run = to_streamed_response_wrapper(
            docling_chunker.run,
        )


class AsyncDoclingChunkerResourceWithStreamingResponse:
    def __init__(self, docling_chunker: AsyncDoclingChunkerResource) -> None:
        self._docling_chunker = docling_chunker

        self.run = async_to_streamed_response_wrapper(
            docling_chunker.run,
        )
