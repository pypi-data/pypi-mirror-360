# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ......_types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ......_compat import cached_property
from ......_resource import SyncAPIResource, AsyncAPIResource
from ......_response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ......_base_client import make_request_options
from ......types.admin.identity.identity_role import IdentityRole

__all__ = ["IdentityResource", "AsyncIdentityResource"]


class IdentityResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> IdentityResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/quarklabsai/quarkupy#accessing-raw-response-data-eg-headers
        """
        return IdentityResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> IdentityResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/quarklabsai/quarkupy#with_streaming_response
        """
        return IdentityResourceWithStreamingResponse(self)

    def add(
        self,
        identity_id: str,
        *,
        id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> IdentityRole:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        if not identity_id:
            raise ValueError(f"Expected a non-empty value for `identity_id` but received {identity_id!r}")
        extra_headers = {"Accept": "application/json; charset=utf-8", **(extra_headers or {})}
        return self._put(
            f"/admin/identity/roles/{id}/members/identity/{identity_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=IdentityRole,
        )

    def remove(
        self,
        identity_id: str,
        *,
        id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> IdentityRole:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        if not identity_id:
            raise ValueError(f"Expected a non-empty value for `identity_id` but received {identity_id!r}")
        extra_headers = {"Accept": "application/json; charset=utf-8", **(extra_headers or {})}
        return self._delete(
            f"/admin/identity/roles/{id}/members/identity/{identity_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=IdentityRole,
        )


class AsyncIdentityResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncIdentityResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/quarklabsai/quarkupy#accessing-raw-response-data-eg-headers
        """
        return AsyncIdentityResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncIdentityResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/quarklabsai/quarkupy#with_streaming_response
        """
        return AsyncIdentityResourceWithStreamingResponse(self)

    async def add(
        self,
        identity_id: str,
        *,
        id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> IdentityRole:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        if not identity_id:
            raise ValueError(f"Expected a non-empty value for `identity_id` but received {identity_id!r}")
        extra_headers = {"Accept": "application/json; charset=utf-8", **(extra_headers or {})}
        return await self._put(
            f"/admin/identity/roles/{id}/members/identity/{identity_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=IdentityRole,
        )

    async def remove(
        self,
        identity_id: str,
        *,
        id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> IdentityRole:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        if not identity_id:
            raise ValueError(f"Expected a non-empty value for `identity_id` but received {identity_id!r}")
        extra_headers = {"Accept": "application/json; charset=utf-8", **(extra_headers or {})}
        return await self._delete(
            f"/admin/identity/roles/{id}/members/identity/{identity_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=IdentityRole,
        )


class IdentityResourceWithRawResponse:
    def __init__(self, identity: IdentityResource) -> None:
        self._identity = identity

        self.add = to_raw_response_wrapper(
            identity.add,
        )
        self.remove = to_raw_response_wrapper(
            identity.remove,
        )


class AsyncIdentityResourceWithRawResponse:
    def __init__(self, identity: AsyncIdentityResource) -> None:
        self._identity = identity

        self.add = async_to_raw_response_wrapper(
            identity.add,
        )
        self.remove = async_to_raw_response_wrapper(
            identity.remove,
        )


class IdentityResourceWithStreamingResponse:
    def __init__(self, identity: IdentityResource) -> None:
        self._identity = identity

        self.add = to_streamed_response_wrapper(
            identity.add,
        )
        self.remove = to_streamed_response_wrapper(
            identity.remove,
        )


class AsyncIdentityResourceWithStreamingResponse:
    def __init__(self, identity: AsyncIdentityResource) -> None:
        self._identity = identity

        self.add = async_to_streamed_response_wrapper(
            identity.add,
        )
        self.remove = async_to_streamed_response_wrapper(
            identity.remove,
        )
