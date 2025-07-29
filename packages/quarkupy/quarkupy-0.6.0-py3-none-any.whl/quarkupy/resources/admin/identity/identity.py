# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from . import identity_ as identity
from ...._compat import cached_property
from .roles.roles import (
    RolesResource,
    AsyncRolesResource,
    RolesResourceWithRawResponse,
    AsyncRolesResourceWithRawResponse,
    RolesResourceWithStreamingResponse,
    AsyncRolesResourceWithStreamingResponse,
)
from ...._resource import SyncAPIResource, AsyncAPIResource

__all__ = ["IdentityResource", "AsyncIdentityResource"]


class IdentityResource(SyncAPIResource):
    @cached_property
    def identity(self) -> identity.IdentityResource:
        return identity.IdentityResource(self._client)

    @cached_property
    def roles(self) -> RolesResource:
        return RolesResource(self._client)

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


class AsyncIdentityResource(AsyncAPIResource):
    @cached_property
    def identity(self) -> identity.AsyncIdentityResource:
        return identity.AsyncIdentityResource(self._client)

    @cached_property
    def roles(self) -> AsyncRolesResource:
        return AsyncRolesResource(self._client)

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


class IdentityResourceWithRawResponse:
    def __init__(self, identity: IdentityResource) -> None:
        self._identity = identity

    @cached_property
    def identity(self) -> identity.IdentityResourceWithRawResponse:
        return identity.IdentityResourceWithRawResponse(self._identity.identity)

    @cached_property
    def roles(self) -> RolesResourceWithRawResponse:
        return RolesResourceWithRawResponse(self._identity.roles)


class AsyncIdentityResourceWithRawResponse:
    def __init__(self, identity: AsyncIdentityResource) -> None:
        self._identity = identity

    @cached_property
    def identity(self) -> identity.AsyncIdentityResourceWithRawResponse:
        return identity.AsyncIdentityResourceWithRawResponse(self._identity.identity)

    @cached_property
    def roles(self) -> AsyncRolesResourceWithRawResponse:
        return AsyncRolesResourceWithRawResponse(self._identity.roles)


class IdentityResourceWithStreamingResponse:
    def __init__(self, identity: IdentityResource) -> None:
        self._identity = identity

    @cached_property
    def identity(self) -> identity.IdentityResourceWithStreamingResponse:
        return identity.IdentityResourceWithStreamingResponse(self._identity.identity)

    @cached_property
    def roles(self) -> RolesResourceWithStreamingResponse:
        return RolesResourceWithStreamingResponse(self._identity.roles)


class AsyncIdentityResourceWithStreamingResponse:
    def __init__(self, identity: AsyncIdentityResource) -> None:
        self._identity = identity

    @cached_property
    def identity(self) -> identity.AsyncIdentityResourceWithStreamingResponse:
        return identity.AsyncIdentityResourceWithStreamingResponse(self._identity.identity)

    @cached_property
    def roles(self) -> AsyncRolesResourceWithStreamingResponse:
        return AsyncRolesResourceWithStreamingResponse(self._identity.roles)
