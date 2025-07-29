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
from ......types.worker.registry.quark.transformer import context_classifier_prompt_run_params

__all__ = ["ContextClassifierPromptResource", "AsyncContextClassifierPromptResource"]


class ContextClassifierPromptResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ContextClassifierPromptResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/quarklabsai/quarkupy#accessing-raw-response-data-eg-headers
        """
        return ContextClassifierPromptResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ContextClassifierPromptResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/quarklabsai/quarkupy#with_streaming_response
        """
        return ContextClassifierPromptResourceWithStreamingResponse(self)

    def run(
        self,
        *,
        classifier_ids: List[str],
        flow_id: str,
        ipc_dataset_id: str,
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
            "/worker/registry/quark/transformer/context_classifier_prompt/run",
            body=maybe_transform(
                {
                    "classifier_ids": classifier_ids,
                    "flow_id": flow_id,
                    "ipc_dataset_id": ipc_dataset_id,
                    "opt_rendered_col": opt_rendered_col,
                },
                context_classifier_prompt_run_params.ContextClassifierPromptRunParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=QuarkHistoryItem,
        )


class AsyncContextClassifierPromptResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncContextClassifierPromptResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/quarklabsai/quarkupy#accessing-raw-response-data-eg-headers
        """
        return AsyncContextClassifierPromptResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncContextClassifierPromptResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/quarklabsai/quarkupy#with_streaming_response
        """
        return AsyncContextClassifierPromptResourceWithStreamingResponse(self)

    async def run(
        self,
        *,
        classifier_ids: List[str],
        flow_id: str,
        ipc_dataset_id: str,
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
            "/worker/registry/quark/transformer/context_classifier_prompt/run",
            body=await async_maybe_transform(
                {
                    "classifier_ids": classifier_ids,
                    "flow_id": flow_id,
                    "ipc_dataset_id": ipc_dataset_id,
                    "opt_rendered_col": opt_rendered_col,
                },
                context_classifier_prompt_run_params.ContextClassifierPromptRunParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=QuarkHistoryItem,
        )


class ContextClassifierPromptResourceWithRawResponse:
    def __init__(self, context_classifier_prompt: ContextClassifierPromptResource) -> None:
        self._context_classifier_prompt = context_classifier_prompt

        self.run = to_raw_response_wrapper(
            context_classifier_prompt.run,
        )


class AsyncContextClassifierPromptResourceWithRawResponse:
    def __init__(self, context_classifier_prompt: AsyncContextClassifierPromptResource) -> None:
        self._context_classifier_prompt = context_classifier_prompt

        self.run = async_to_raw_response_wrapper(
            context_classifier_prompt.run,
        )


class ContextClassifierPromptResourceWithStreamingResponse:
    def __init__(self, context_classifier_prompt: ContextClassifierPromptResource) -> None:
        self._context_classifier_prompt = context_classifier_prompt

        self.run = to_streamed_response_wrapper(
            context_classifier_prompt.run,
        )


class AsyncContextClassifierPromptResourceWithStreamingResponse:
    def __init__(self, context_classifier_prompt: AsyncContextClassifierPromptResource) -> None:
        self._context_classifier_prompt = context_classifier_prompt

        self.run = async_to_streamed_response_wrapper(
            context_classifier_prompt.run,
        )
