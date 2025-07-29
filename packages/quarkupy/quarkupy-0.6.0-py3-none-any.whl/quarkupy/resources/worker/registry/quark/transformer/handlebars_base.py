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
from ......types.worker.registry.quark.transformer import handlebars_base_run_params

__all__ = ["HandlebarsBaseResource", "AsyncHandlebarsBaseResource"]


class HandlebarsBaseResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> HandlebarsBaseResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/quarklabsai/quarkupy#accessing-raw-response-data-eg-headers
        """
        return HandlebarsBaseResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> HandlebarsBaseResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/quarklabsai/quarkupy#with_streaming_response
        """
        return HandlebarsBaseResourceWithStreamingResponse(self)

    def run(
        self,
        *,
        input_columns: List[str],
        ipc_dataset_id: str,
        lattice_id: str,
        template: str,
        opt_rendered_col: str | NotGiven = NOT_GIVEN,
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
            "/worker/registry/quark/transformer/handlebars_base/run",
            body=maybe_transform(
                {
                    "input_columns": input_columns,
                    "ipc_dataset_id": ipc_dataset_id,
                    "lattice_id": lattice_id,
                    "template": template,
                    "opt_rendered_col": opt_rendered_col,
                },
                handlebars_base_run_params.HandlebarsBaseRunParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=QuarkHistoryItem,
        )


class AsyncHandlebarsBaseResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncHandlebarsBaseResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/quarklabsai/quarkupy#accessing-raw-response-data-eg-headers
        """
        return AsyncHandlebarsBaseResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncHandlebarsBaseResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/quarklabsai/quarkupy#with_streaming_response
        """
        return AsyncHandlebarsBaseResourceWithStreamingResponse(self)

    async def run(
        self,
        *,
        input_columns: List[str],
        ipc_dataset_id: str,
        lattice_id: str,
        template: str,
        opt_rendered_col: str | NotGiven = NOT_GIVEN,
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
            "/worker/registry/quark/transformer/handlebars_base/run",
            body=await async_maybe_transform(
                {
                    "input_columns": input_columns,
                    "ipc_dataset_id": ipc_dataset_id,
                    "lattice_id": lattice_id,
                    "template": template,
                    "opt_rendered_col": opt_rendered_col,
                },
                handlebars_base_run_params.HandlebarsBaseRunParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=QuarkHistoryItem,
        )


class HandlebarsBaseResourceWithRawResponse:
    def __init__(self, handlebars_base: HandlebarsBaseResource) -> None:
        self._handlebars_base = handlebars_base

        self.run = to_raw_response_wrapper(
            handlebars_base.run,
        )


class AsyncHandlebarsBaseResourceWithRawResponse:
    def __init__(self, handlebars_base: AsyncHandlebarsBaseResource) -> None:
        self._handlebars_base = handlebars_base

        self.run = async_to_raw_response_wrapper(
            handlebars_base.run,
        )


class HandlebarsBaseResourceWithStreamingResponse:
    def __init__(self, handlebars_base: HandlebarsBaseResource) -> None:
        self._handlebars_base = handlebars_base

        self.run = to_streamed_response_wrapper(
            handlebars_base.run,
        )


class AsyncHandlebarsBaseResourceWithStreamingResponse:
    def __init__(self, handlebars_base: AsyncHandlebarsBaseResource) -> None:
        self._handlebars_base = handlebars_base

        self.run = async_to_streamed_response_wrapper(
            handlebars_base.run,
        )
