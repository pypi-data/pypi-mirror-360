# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

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
from ...types.worker import agent_chat_rag_demo_params
from ...types.worker.agent_retrieve_response import AgentRetrieveResponse

__all__ = ["AgentResource", "AsyncAgentResource"]


class AgentResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AgentResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/quarklabsai/quarkupy#accessing-raw-response-data-eg-headers
        """
        return AgentResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AgentResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/quarklabsai/quarkupy#with_streaming_response
        """
        return AgentResourceWithStreamingResponse(self)

    def retrieve(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AgentRetrieveResponse:
        extra_headers = {"Accept": "application/json; charset=utf-8", **(extra_headers or {})}
        return self._get(
            "/worker/agent",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AgentRetrieveResponse,
        )

    def chat_rag_demo(
        self,
        *,
        openai_api_key: str,
        query: str,
        table_name: str,
        search_limit: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "application/json; charset=utf-8", **(extra_headers or {})}
        return self._post(
            "/worker/agent/chat_rag_demo",
            body=maybe_transform(
                {
                    "openai_api_key": openai_api_key,
                    "query": query,
                    "table_name": table_name,
                    "search_limit": search_limit,
                },
                agent_chat_rag_demo_params.AgentChatRagDemoParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )


class AsyncAgentResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncAgentResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/quarklabsai/quarkupy#accessing-raw-response-data-eg-headers
        """
        return AsyncAgentResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncAgentResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/quarklabsai/quarkupy#with_streaming_response
        """
        return AsyncAgentResourceWithStreamingResponse(self)

    async def retrieve(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AgentRetrieveResponse:
        extra_headers = {"Accept": "application/json; charset=utf-8", **(extra_headers or {})}
        return await self._get(
            "/worker/agent",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AgentRetrieveResponse,
        )

    async def chat_rag_demo(
        self,
        *,
        openai_api_key: str,
        query: str,
        table_name: str,
        search_limit: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "application/json; charset=utf-8", **(extra_headers or {})}
        return await self._post(
            "/worker/agent/chat_rag_demo",
            body=await async_maybe_transform(
                {
                    "openai_api_key": openai_api_key,
                    "query": query,
                    "table_name": table_name,
                    "search_limit": search_limit,
                },
                agent_chat_rag_demo_params.AgentChatRagDemoParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )


class AgentResourceWithRawResponse:
    def __init__(self, agent: AgentResource) -> None:
        self._agent = agent

        self.retrieve = to_raw_response_wrapper(
            agent.retrieve,
        )
        self.chat_rag_demo = to_raw_response_wrapper(
            agent.chat_rag_demo,
        )


class AsyncAgentResourceWithRawResponse:
    def __init__(self, agent: AsyncAgentResource) -> None:
        self._agent = agent

        self.retrieve = async_to_raw_response_wrapper(
            agent.retrieve,
        )
        self.chat_rag_demo = async_to_raw_response_wrapper(
            agent.chat_rag_demo,
        )


class AgentResourceWithStreamingResponse:
    def __init__(self, agent: AgentResource) -> None:
        self._agent = agent

        self.retrieve = to_streamed_response_wrapper(
            agent.retrieve,
        )
        self.chat_rag_demo = to_streamed_response_wrapper(
            agent.chat_rag_demo,
        )


class AsyncAgentResourceWithStreamingResponse:
    def __init__(self, agent: AsyncAgentResource) -> None:
        self._agent = agent

        self.retrieve = async_to_streamed_response_wrapper(
            agent.retrieve,
        )
        self.chat_rag_demo = async_to_streamed_response_wrapper(
            agent.chat_rag_demo,
        )
