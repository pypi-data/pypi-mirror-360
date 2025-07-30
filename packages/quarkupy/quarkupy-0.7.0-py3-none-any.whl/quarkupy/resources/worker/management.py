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
from ...types.worker import management_retrieve_tokio_params
from ...types.admin.identity.identity_model import IdentityModel
from ...types.context.success_response_message import SuccessResponseMessage
from ...types.worker.management_retrieve_response import ManagementRetrieveResponse
from ...types.worker.management_retrieve_tokio_response import ManagementRetrieveTokioResponse
from ...types.worker.management_retrieve_python_status_response import ManagementRetrievePythonStatusResponse

__all__ = ["ManagementResource", "AsyncManagementResource"]


class ManagementResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ManagementResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/quarklabsai/quarkupy#accessing-raw-response-data-eg-headers
        """
        return ManagementResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ManagementResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/quarklabsai/quarkupy#with_streaming_response
        """
        return ManagementResourceWithStreamingResponse(self)

    def retrieve(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ManagementRetrieveResponse:
        extra_headers = {"Accept": "application/json; charset=utf-8", **(extra_headers or {})}
        return self._get(
            "/worker/management",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ManagementRetrieveResponse,
        )

    def ping(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SuccessResponseMessage:
        extra_headers = {"Accept": "application/json; charset=utf-8", **(extra_headers or {})}
        return self._post(
            "/worker/management/ping",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SuccessResponseMessage,
        )

    def retrieve_auth_status(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> IdentityModel:
        extra_headers = {"Accept": "application/json; charset=utf-8", **(extra_headers or {})}
        return self._get(
            "/worker/management/auth_status",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=IdentityModel,
        )

    def retrieve_python_status(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ManagementRetrievePythonStatusResponse:
        extra_headers = {"Accept": "application/json; charset=utf-8", **(extra_headers or {})}
        return self._get(
            "/worker/management/python_status",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ManagementRetrievePythonStatusResponse,
        )

    def retrieve_tokio(
        self,
        *,
        with_dump: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ManagementRetrieveTokioResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "application/json; charset=utf-8", **(extra_headers or {})}
        return self._get(
            "/worker/management/tokio",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"with_dump": with_dump}, management_retrieve_tokio_params.ManagementRetrieveTokioParams
                ),
            ),
            cast_to=ManagementRetrieveTokioResponse,
        )


class AsyncManagementResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncManagementResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/quarklabsai/quarkupy#accessing-raw-response-data-eg-headers
        """
        return AsyncManagementResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncManagementResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/quarklabsai/quarkupy#with_streaming_response
        """
        return AsyncManagementResourceWithStreamingResponse(self)

    async def retrieve(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ManagementRetrieveResponse:
        extra_headers = {"Accept": "application/json; charset=utf-8", **(extra_headers or {})}
        return await self._get(
            "/worker/management",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ManagementRetrieveResponse,
        )

    async def ping(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SuccessResponseMessage:
        extra_headers = {"Accept": "application/json; charset=utf-8", **(extra_headers or {})}
        return await self._post(
            "/worker/management/ping",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SuccessResponseMessage,
        )

    async def retrieve_auth_status(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> IdentityModel:
        extra_headers = {"Accept": "application/json; charset=utf-8", **(extra_headers or {})}
        return await self._get(
            "/worker/management/auth_status",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=IdentityModel,
        )

    async def retrieve_python_status(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ManagementRetrievePythonStatusResponse:
        extra_headers = {"Accept": "application/json; charset=utf-8", **(extra_headers or {})}
        return await self._get(
            "/worker/management/python_status",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ManagementRetrievePythonStatusResponse,
        )

    async def retrieve_tokio(
        self,
        *,
        with_dump: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ManagementRetrieveTokioResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "application/json; charset=utf-8", **(extra_headers or {})}
        return await self._get(
            "/worker/management/tokio",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"with_dump": with_dump}, management_retrieve_tokio_params.ManagementRetrieveTokioParams
                ),
            ),
            cast_to=ManagementRetrieveTokioResponse,
        )


class ManagementResourceWithRawResponse:
    def __init__(self, management: ManagementResource) -> None:
        self._management = management

        self.retrieve = to_raw_response_wrapper(
            management.retrieve,
        )
        self.ping = to_raw_response_wrapper(
            management.ping,
        )
        self.retrieve_auth_status = to_raw_response_wrapper(
            management.retrieve_auth_status,
        )
        self.retrieve_python_status = to_raw_response_wrapper(
            management.retrieve_python_status,
        )
        self.retrieve_tokio = to_raw_response_wrapper(
            management.retrieve_tokio,
        )


class AsyncManagementResourceWithRawResponse:
    def __init__(self, management: AsyncManagementResource) -> None:
        self._management = management

        self.retrieve = async_to_raw_response_wrapper(
            management.retrieve,
        )
        self.ping = async_to_raw_response_wrapper(
            management.ping,
        )
        self.retrieve_auth_status = async_to_raw_response_wrapper(
            management.retrieve_auth_status,
        )
        self.retrieve_python_status = async_to_raw_response_wrapper(
            management.retrieve_python_status,
        )
        self.retrieve_tokio = async_to_raw_response_wrapper(
            management.retrieve_tokio,
        )


class ManagementResourceWithStreamingResponse:
    def __init__(self, management: ManagementResource) -> None:
        self._management = management

        self.retrieve = to_streamed_response_wrapper(
            management.retrieve,
        )
        self.ping = to_streamed_response_wrapper(
            management.ping,
        )
        self.retrieve_auth_status = to_streamed_response_wrapper(
            management.retrieve_auth_status,
        )
        self.retrieve_python_status = to_streamed_response_wrapper(
            management.retrieve_python_status,
        )
        self.retrieve_tokio = to_streamed_response_wrapper(
            management.retrieve_tokio,
        )


class AsyncManagementResourceWithStreamingResponse:
    def __init__(self, management: AsyncManagementResource) -> None:
        self._management = management

        self.retrieve = async_to_streamed_response_wrapper(
            management.retrieve,
        )
        self.ping = async_to_streamed_response_wrapper(
            management.ping,
        )
        self.retrieve_auth_status = async_to_streamed_response_wrapper(
            management.retrieve_auth_status,
        )
        self.retrieve_python_status = async_to_streamed_response_wrapper(
            management.retrieve_python_status,
        )
        self.retrieve_tokio = async_to_streamed_response_wrapper(
            management.retrieve_tokio,
        )
