# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from .lattice import (
    LatticeResource,
    AsyncLatticeResource,
    LatticeResourceWithRawResponse,
    AsyncLatticeResourceWithRawResponse,
    LatticeResourceWithStreamingResponse,
    AsyncLatticeResourceWithStreamingResponse,
)
from ...._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ...._compat import cached_property
from .quark.quark import (
    QuarkResource,
    AsyncQuarkResource,
    QuarkResourceWithRawResponse,
    AsyncQuarkResourceWithRawResponse,
    QuarkResourceWithStreamingResponse,
    AsyncQuarkResourceWithStreamingResponse,
)
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ...._base_client import make_request_options
from ....types.worker.registry_list_response import RegistryListResponse

__all__ = ["RegistryResource", "AsyncRegistryResource"]


class RegistryResource(SyncAPIResource):
    @cached_property
    def quark(self) -> QuarkResource:
        return QuarkResource(self._client)

    @cached_property
    def lattice(self) -> LatticeResource:
        return LatticeResource(self._client)

    @cached_property
    def with_raw_response(self) -> RegistryResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/quarklabsai/quarkupy#accessing-raw-response-data-eg-headers
        """
        return RegistryResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> RegistryResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/quarklabsai/quarkupy#with_streaming_response
        """
        return RegistryResourceWithStreamingResponse(self)

    def list(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> RegistryListResponse:
        extra_headers = {"Accept": "application/json; charset=utf-8", **(extra_headers or {})}
        return self._get(
            "/worker/registry",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RegistryListResponse,
        )


class AsyncRegistryResource(AsyncAPIResource):
    @cached_property
    def quark(self) -> AsyncQuarkResource:
        return AsyncQuarkResource(self._client)

    @cached_property
    def lattice(self) -> AsyncLatticeResource:
        return AsyncLatticeResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncRegistryResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/quarklabsai/quarkupy#accessing-raw-response-data-eg-headers
        """
        return AsyncRegistryResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncRegistryResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/quarklabsai/quarkupy#with_streaming_response
        """
        return AsyncRegistryResourceWithStreamingResponse(self)

    async def list(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> RegistryListResponse:
        extra_headers = {"Accept": "application/json; charset=utf-8", **(extra_headers or {})}
        return await self._get(
            "/worker/registry",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RegistryListResponse,
        )


class RegistryResourceWithRawResponse:
    def __init__(self, registry: RegistryResource) -> None:
        self._registry = registry

        self.list = to_raw_response_wrapper(
            registry.list,
        )

    @cached_property
    def quark(self) -> QuarkResourceWithRawResponse:
        return QuarkResourceWithRawResponse(self._registry.quark)

    @cached_property
    def lattice(self) -> LatticeResourceWithRawResponse:
        return LatticeResourceWithRawResponse(self._registry.lattice)


class AsyncRegistryResourceWithRawResponse:
    def __init__(self, registry: AsyncRegistryResource) -> None:
        self._registry = registry

        self.list = async_to_raw_response_wrapper(
            registry.list,
        )

    @cached_property
    def quark(self) -> AsyncQuarkResourceWithRawResponse:
        return AsyncQuarkResourceWithRawResponse(self._registry.quark)

    @cached_property
    def lattice(self) -> AsyncLatticeResourceWithRawResponse:
        return AsyncLatticeResourceWithRawResponse(self._registry.lattice)


class RegistryResourceWithStreamingResponse:
    def __init__(self, registry: RegistryResource) -> None:
        self._registry = registry

        self.list = to_streamed_response_wrapper(
            registry.list,
        )

    @cached_property
    def quark(self) -> QuarkResourceWithStreamingResponse:
        return QuarkResourceWithStreamingResponse(self._registry.quark)

    @cached_property
    def lattice(self) -> LatticeResourceWithStreamingResponse:
        return LatticeResourceWithStreamingResponse(self._registry.lattice)


class AsyncRegistryResourceWithStreamingResponse:
    def __init__(self, registry: AsyncRegistryResource) -> None:
        self._registry = registry

        self.list = async_to_streamed_response_wrapper(
            registry.list,
        )

    @cached_property
    def quark(self) -> AsyncQuarkResourceWithStreamingResponse:
        return AsyncQuarkResourceWithStreamingResponse(self._registry.quark)

    @cached_property
    def lattice(self) -> AsyncLatticeResourceWithStreamingResponse:
        return AsyncLatticeResourceWithStreamingResponse(self._registry.lattice)
