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
from ......types.worker.registry.quark.ai import openai_completion_base_run_params
from ......types.history.quark_history_item import QuarkHistoryItem

__all__ = ["OpenAICompletionBaseResource", "AsyncOpenAICompletionBaseResource"]


class OpenAICompletionBaseResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> OpenAICompletionBaseResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/quarklabsai/quarkupy#accessing-raw-response-data-eg-headers
        """
        return OpenAICompletionBaseResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> OpenAICompletionBaseResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/quarklabsai/quarkupy#with_streaming_response
        """
        return OpenAICompletionBaseResourceWithStreamingResponse(self)

    def run(
        self,
        *,
        api_key: str,
        ipc_dataset_id: str,
        lattice_id: str,
        opt_explode_json: bool | NotGiven = NOT_GIVEN,
        opt_json_output: bool | NotGiven = NOT_GIVEN,
        opt_max_output_tokens: int | NotGiven = NOT_GIVEN,
        opt_model_name: str | NotGiven = NOT_GIVEN,
        opt_prompt_column: str | NotGiven = NOT_GIVEN,
        opt_system_prompt: str | NotGiven = NOT_GIVEN,
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
            "/worker/registry/quark/ai/openai_completion_base/run",
            body=maybe_transform(
                {
                    "api_key": api_key,
                    "ipc_dataset_id": ipc_dataset_id,
                    "lattice_id": lattice_id,
                    "opt_explode_json": opt_explode_json,
                    "opt_json_output": opt_json_output,
                    "opt_max_output_tokens": opt_max_output_tokens,
                    "opt_model_name": opt_model_name,
                    "opt_prompt_column": opt_prompt_column,
                    "opt_system_prompt": opt_system_prompt,
                },
                openai_completion_base_run_params.OpenAICompletionBaseRunParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=QuarkHistoryItem,
        )


class AsyncOpenAICompletionBaseResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncOpenAICompletionBaseResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/quarklabsai/quarkupy#accessing-raw-response-data-eg-headers
        """
        return AsyncOpenAICompletionBaseResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncOpenAICompletionBaseResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/quarklabsai/quarkupy#with_streaming_response
        """
        return AsyncOpenAICompletionBaseResourceWithStreamingResponse(self)

    async def run(
        self,
        *,
        api_key: str,
        ipc_dataset_id: str,
        lattice_id: str,
        opt_explode_json: bool | NotGiven = NOT_GIVEN,
        opt_json_output: bool | NotGiven = NOT_GIVEN,
        opt_max_output_tokens: int | NotGiven = NOT_GIVEN,
        opt_model_name: str | NotGiven = NOT_GIVEN,
        opt_prompt_column: str | NotGiven = NOT_GIVEN,
        opt_system_prompt: str | NotGiven = NOT_GIVEN,
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
            "/worker/registry/quark/ai/openai_completion_base/run",
            body=await async_maybe_transform(
                {
                    "api_key": api_key,
                    "ipc_dataset_id": ipc_dataset_id,
                    "lattice_id": lattice_id,
                    "opt_explode_json": opt_explode_json,
                    "opt_json_output": opt_json_output,
                    "opt_max_output_tokens": opt_max_output_tokens,
                    "opt_model_name": opt_model_name,
                    "opt_prompt_column": opt_prompt_column,
                    "opt_system_prompt": opt_system_prompt,
                },
                openai_completion_base_run_params.OpenAICompletionBaseRunParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=QuarkHistoryItem,
        )


class OpenAICompletionBaseResourceWithRawResponse:
    def __init__(self, openai_completion_base: OpenAICompletionBaseResource) -> None:
        self._openai_completion_base = openai_completion_base

        self.run = to_raw_response_wrapper(
            openai_completion_base.run,
        )


class AsyncOpenAICompletionBaseResourceWithRawResponse:
    def __init__(self, openai_completion_base: AsyncOpenAICompletionBaseResource) -> None:
        self._openai_completion_base = openai_completion_base

        self.run = async_to_raw_response_wrapper(
            openai_completion_base.run,
        )


class OpenAICompletionBaseResourceWithStreamingResponse:
    def __init__(self, openai_completion_base: OpenAICompletionBaseResource) -> None:
        self._openai_completion_base = openai_completion_base

        self.run = to_streamed_response_wrapper(
            openai_completion_base.run,
        )


class AsyncOpenAICompletionBaseResourceWithStreamingResponse:
    def __init__(self, openai_completion_base: AsyncOpenAICompletionBaseResource) -> None:
        self._openai_completion_base = openai_completion_base

        self.run = async_to_streamed_response_wrapper(
            openai_completion_base.run,
        )
