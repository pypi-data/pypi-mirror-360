# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..types import authorize_retrieve_params
from .._types import NOT_GIVEN, Body, Query, Headers, NoneType, NotGiven
from .._utils import maybe_transform, async_maybe_transform
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options

__all__ = ["AuthorizeResource", "AsyncAuthorizeResource"]


class AuthorizeResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AuthorizeResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/quarklabsai/quarkupy#accessing-raw-response-data-eg-headers
        """
        return AuthorizeResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AuthorizeResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/quarklabsai/quarkupy#with_streaming_response
        """
        return AuthorizeResourceWithStreamingResponse(self)

    def retrieve(
        self,
        *,
        code: str,
        _state: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._get(
            "/authorize",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "code": code,
                        "_state": _state,
                    },
                    authorize_retrieve_params.AuthorizeRetrieveParams,
                ),
            ),
            cast_to=NoneType,
        )

    def logout(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._get(
            "/authorize/logout",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )


class AsyncAuthorizeResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncAuthorizeResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/quarklabsai/quarkupy#accessing-raw-response-data-eg-headers
        """
        return AsyncAuthorizeResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncAuthorizeResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/quarklabsai/quarkupy#with_streaming_response
        """
        return AsyncAuthorizeResourceWithStreamingResponse(self)

    async def retrieve(
        self,
        *,
        code: str,
        _state: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._get(
            "/authorize",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "code": code,
                        "_state": _state,
                    },
                    authorize_retrieve_params.AuthorizeRetrieveParams,
                ),
            ),
            cast_to=NoneType,
        )

    async def logout(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._get(
            "/authorize/logout",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )


class AuthorizeResourceWithRawResponse:
    def __init__(self, authorize: AuthorizeResource) -> None:
        self._authorize = authorize

        self.retrieve = to_raw_response_wrapper(
            authorize.retrieve,
        )
        self.logout = to_raw_response_wrapper(
            authorize.logout,
        )


class AsyncAuthorizeResourceWithRawResponse:
    def __init__(self, authorize: AsyncAuthorizeResource) -> None:
        self._authorize = authorize

        self.retrieve = async_to_raw_response_wrapper(
            authorize.retrieve,
        )
        self.logout = async_to_raw_response_wrapper(
            authorize.logout,
        )


class AuthorizeResourceWithStreamingResponse:
    def __init__(self, authorize: AuthorizeResource) -> None:
        self._authorize = authorize

        self.retrieve = to_streamed_response_wrapper(
            authorize.retrieve,
        )
        self.logout = to_streamed_response_wrapper(
            authorize.logout,
        )


class AsyncAuthorizeResourceWithStreamingResponse:
    def __init__(self, authorize: AsyncAuthorizeResource) -> None:
        self._authorize = authorize

        self.retrieve = async_to_streamed_response_wrapper(
            authorize.retrieve,
        )
        self.logout = async_to_streamed_response_wrapper(
            authorize.logout,
        )
