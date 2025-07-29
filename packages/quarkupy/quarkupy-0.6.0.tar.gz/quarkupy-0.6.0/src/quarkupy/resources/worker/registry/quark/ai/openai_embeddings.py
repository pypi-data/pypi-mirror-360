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
from ......types.worker.registry.quark.ai import openai_embedding_run_params
from ......types.history.quark_history_item import QuarkHistoryItem

__all__ = ["OpenAIEmbeddingsResource", "AsyncOpenAIEmbeddingsResource"]


class OpenAIEmbeddingsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> OpenAIEmbeddingsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/quarklabsai/quarkupy#accessing-raw-response-data-eg-headers
        """
        return OpenAIEmbeddingsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> OpenAIEmbeddingsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/quarklabsai/quarkupy#with_streaming_response
        """
        return OpenAIEmbeddingsResourceWithStreamingResponse(self)

    def run(
        self,
        *,
        api_key: str,
        ipc_dataset_id: str,
        lattice_id: str,
        opt_model_name: str | NotGiven = NOT_GIVEN,
        opt_num_embeddings: int | NotGiven = NOT_GIVEN,
        opt_text_additional_embed_columns: List[str] | NotGiven = NOT_GIVEN,
        opt_text_column_name: str | NotGiven = NOT_GIVEN,
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
            "/worker/registry/quark/ai/openai_embeddings/run",
            body=maybe_transform(
                {
                    "api_key": api_key,
                    "ipc_dataset_id": ipc_dataset_id,
                    "lattice_id": lattice_id,
                    "opt_model_name": opt_model_name,
                    "opt_num_embeddings": opt_num_embeddings,
                    "opt_text_additional_embed_columns": opt_text_additional_embed_columns,
                    "opt_text_column_name": opt_text_column_name,
                },
                openai_embedding_run_params.OpenAIEmbeddingRunParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=QuarkHistoryItem,
        )


class AsyncOpenAIEmbeddingsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncOpenAIEmbeddingsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/quarklabsai/quarkupy#accessing-raw-response-data-eg-headers
        """
        return AsyncOpenAIEmbeddingsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncOpenAIEmbeddingsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/quarklabsai/quarkupy#with_streaming_response
        """
        return AsyncOpenAIEmbeddingsResourceWithStreamingResponse(self)

    async def run(
        self,
        *,
        api_key: str,
        ipc_dataset_id: str,
        lattice_id: str,
        opt_model_name: str | NotGiven = NOT_GIVEN,
        opt_num_embeddings: int | NotGiven = NOT_GIVEN,
        opt_text_additional_embed_columns: List[str] | NotGiven = NOT_GIVEN,
        opt_text_column_name: str | NotGiven = NOT_GIVEN,
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
            "/worker/registry/quark/ai/openai_embeddings/run",
            body=await async_maybe_transform(
                {
                    "api_key": api_key,
                    "ipc_dataset_id": ipc_dataset_id,
                    "lattice_id": lattice_id,
                    "opt_model_name": opt_model_name,
                    "opt_num_embeddings": opt_num_embeddings,
                    "opt_text_additional_embed_columns": opt_text_additional_embed_columns,
                    "opt_text_column_name": opt_text_column_name,
                },
                openai_embedding_run_params.OpenAIEmbeddingRunParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=QuarkHistoryItem,
        )


class OpenAIEmbeddingsResourceWithRawResponse:
    def __init__(self, openai_embeddings: OpenAIEmbeddingsResource) -> None:
        self._openai_embeddings = openai_embeddings

        self.run = to_raw_response_wrapper(
            openai_embeddings.run,
        )


class AsyncOpenAIEmbeddingsResourceWithRawResponse:
    def __init__(self, openai_embeddings: AsyncOpenAIEmbeddingsResource) -> None:
        self._openai_embeddings = openai_embeddings

        self.run = async_to_raw_response_wrapper(
            openai_embeddings.run,
        )


class OpenAIEmbeddingsResourceWithStreamingResponse:
    def __init__(self, openai_embeddings: OpenAIEmbeddingsResource) -> None:
        self._openai_embeddings = openai_embeddings

        self.run = to_streamed_response_wrapper(
            openai_embeddings.run,
        )


class AsyncOpenAIEmbeddingsResourceWithStreamingResponse:
    def __init__(self, openai_embeddings: AsyncOpenAIEmbeddingsResource) -> None:
        self._openai_embeddings = openai_embeddings

        self.run = async_to_streamed_response_wrapper(
            openai_embeddings.run,
        )
