# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from .role import (
    RoleResource,
    AsyncRoleResource,
    RoleResourceWithRawResponse,
    AsyncRoleResourceWithRawResponse,
    RoleResourceWithStreamingResponse,
    AsyncRoleResourceWithStreamingResponse,
)
from .identity import (
    IdentityResource,
    AsyncIdentityResource,
    IdentityResourceWithRawResponse,
    AsyncIdentityResourceWithRawResponse,
    IdentityResourceWithStreamingResponse,
    AsyncIdentityResourceWithStreamingResponse,
)
from ......_compat import cached_property
from ......_resource import SyncAPIResource, AsyncAPIResource

__all__ = ["MembersResource", "AsyncMembersResource"]


class MembersResource(SyncAPIResource):
    @cached_property
    def identity(self) -> IdentityResource:
        return IdentityResource(self._client)

    @cached_property
    def role(self) -> RoleResource:
        return RoleResource(self._client)

    @cached_property
    def with_raw_response(self) -> MembersResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/quarklabsai/quarkupy#accessing-raw-response-data-eg-headers
        """
        return MembersResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> MembersResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/quarklabsai/quarkupy#with_streaming_response
        """
        return MembersResourceWithStreamingResponse(self)


class AsyncMembersResource(AsyncAPIResource):
    @cached_property
    def identity(self) -> AsyncIdentityResource:
        return AsyncIdentityResource(self._client)

    @cached_property
    def role(self) -> AsyncRoleResource:
        return AsyncRoleResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncMembersResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/quarklabsai/quarkupy#accessing-raw-response-data-eg-headers
        """
        return AsyncMembersResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncMembersResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/quarklabsai/quarkupy#with_streaming_response
        """
        return AsyncMembersResourceWithStreamingResponse(self)


class MembersResourceWithRawResponse:
    def __init__(self, members: MembersResource) -> None:
        self._members = members

    @cached_property
    def identity(self) -> IdentityResourceWithRawResponse:
        return IdentityResourceWithRawResponse(self._members.identity)

    @cached_property
    def role(self) -> RoleResourceWithRawResponse:
        return RoleResourceWithRawResponse(self._members.role)


class AsyncMembersResourceWithRawResponse:
    def __init__(self, members: AsyncMembersResource) -> None:
        self._members = members

    @cached_property
    def identity(self) -> AsyncIdentityResourceWithRawResponse:
        return AsyncIdentityResourceWithRawResponse(self._members.identity)

    @cached_property
    def role(self) -> AsyncRoleResourceWithRawResponse:
        return AsyncRoleResourceWithRawResponse(self._members.role)


class MembersResourceWithStreamingResponse:
    def __init__(self, members: MembersResource) -> None:
        self._members = members

    @cached_property
    def identity(self) -> IdentityResourceWithStreamingResponse:
        return IdentityResourceWithStreamingResponse(self._members.identity)

    @cached_property
    def role(self) -> RoleResourceWithStreamingResponse:
        return RoleResourceWithStreamingResponse(self._members.role)


class AsyncMembersResourceWithStreamingResponse:
    def __init__(self, members: AsyncMembersResource) -> None:
        self._members = members

    @cached_property
    def identity(self) -> AsyncIdentityResourceWithStreamingResponse:
        return AsyncIdentityResourceWithStreamingResponse(self._members.identity)

    @cached_property
    def role(self) -> AsyncRoleResourceWithStreamingResponse:
        return AsyncRoleResourceWithStreamingResponse(self._members.role)
