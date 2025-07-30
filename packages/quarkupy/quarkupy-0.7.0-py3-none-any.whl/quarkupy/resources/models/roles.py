# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from datetime import datetime

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
from ...types.models import role_update_params, role_update_partial_params
from ...types.models.ml_model_role import MlModelRole
from ...types.models.role_list_response import RoleListResponse
from ...types.context.success_response_message import SuccessResponseMessage

__all__ = ["RolesResource", "AsyncRolesResource"]


class RolesResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> RolesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/quarklabsai/quarkupy#accessing-raw-response-data-eg-headers
        """
        return RolesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> RolesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/quarklabsai/quarkupy#with_streaming_response
        """
        return RolesResourceWithStreamingResponse(self)

    def retrieve(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> MlModelRole:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {"Accept": "application/json; charset=utf-8", **(extra_headers or {})}
        return self._get(
            f"/models/roles/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=MlModelRole,
        )

    def update(
        self,
        *,
        config_override: object,
        model_id: str,
        name: str,
        owned_by_identity_id: str,
        description: str | NotGiven = NOT_GIVEN,
        updated_at: Union[str, datetime] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> MlModelRole:
        """
        Args:
          config_override: # Optional Override for Model Configuration

          model_id: # Associated Model

          name: # Model Role Name

          owned_by_identity_id: # Model Role Owner

          description: # Description

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "application/json; charset=utf-8", **(extra_headers or {})}
        return self._put(
            "/models/roles",
            body=maybe_transform(
                {
                    "config_override": config_override,
                    "model_id": model_id,
                    "name": name,
                    "owned_by_identity_id": owned_by_identity_id,
                    "description": description,
                    "updated_at": updated_at,
                },
                role_update_params.RoleUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=MlModelRole,
        )

    def list(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> RoleListResponse:
        extra_headers = {"Accept": "application/json; charset=utf-8", **(extra_headers or {})}
        return self._get(
            "/models/roles",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RoleListResponse,
        )

    def delete(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SuccessResponseMessage:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {"Accept": "application/json; charset=utf-8", **(extra_headers or {})}
        return self._delete(
            f"/models/roles/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SuccessResponseMessage,
        )

    def retrieve_schema(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        extra_headers = {"Accept": "application/json; charset=utf-8", **(extra_headers or {})}
        return self._get(
            "/models/roles/schema",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    def update_partial(
        self,
        id: str,
        *,
        config_override: object,
        model_id: str,
        name: str,
        owned_by_identity_id: str,
        description: str | NotGiven = NOT_GIVEN,
        updated_at: Union[str, datetime] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> MlModelRole:
        """
        Args:
          config_override: # Optional Override for Model Configuration

          model_id: # Associated Model

          name: # Model Role Name

          owned_by_identity_id: # Model Role Owner

          description: # Description

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {"Accept": "application/json; charset=utf-8", **(extra_headers or {})}
        return self._patch(
            f"/models/roles/{id}",
            body=maybe_transform(
                {
                    "config_override": config_override,
                    "model_id": model_id,
                    "name": name,
                    "owned_by_identity_id": owned_by_identity_id,
                    "description": description,
                    "updated_at": updated_at,
                },
                role_update_partial_params.RoleUpdatePartialParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=MlModelRole,
        )


class AsyncRolesResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncRolesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/quarklabsai/quarkupy#accessing-raw-response-data-eg-headers
        """
        return AsyncRolesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncRolesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/quarklabsai/quarkupy#with_streaming_response
        """
        return AsyncRolesResourceWithStreamingResponse(self)

    async def retrieve(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> MlModelRole:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {"Accept": "application/json; charset=utf-8", **(extra_headers or {})}
        return await self._get(
            f"/models/roles/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=MlModelRole,
        )

    async def update(
        self,
        *,
        config_override: object,
        model_id: str,
        name: str,
        owned_by_identity_id: str,
        description: str | NotGiven = NOT_GIVEN,
        updated_at: Union[str, datetime] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> MlModelRole:
        """
        Args:
          config_override: # Optional Override for Model Configuration

          model_id: # Associated Model

          name: # Model Role Name

          owned_by_identity_id: # Model Role Owner

          description: # Description

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "application/json; charset=utf-8", **(extra_headers or {})}
        return await self._put(
            "/models/roles",
            body=await async_maybe_transform(
                {
                    "config_override": config_override,
                    "model_id": model_id,
                    "name": name,
                    "owned_by_identity_id": owned_by_identity_id,
                    "description": description,
                    "updated_at": updated_at,
                },
                role_update_params.RoleUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=MlModelRole,
        )

    async def list(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> RoleListResponse:
        extra_headers = {"Accept": "application/json; charset=utf-8", **(extra_headers or {})}
        return await self._get(
            "/models/roles",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RoleListResponse,
        )

    async def delete(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SuccessResponseMessage:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {"Accept": "application/json; charset=utf-8", **(extra_headers or {})}
        return await self._delete(
            f"/models/roles/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SuccessResponseMessage,
        )

    async def retrieve_schema(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        extra_headers = {"Accept": "application/json; charset=utf-8", **(extra_headers or {})}
        return await self._get(
            "/models/roles/schema",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    async def update_partial(
        self,
        id: str,
        *,
        config_override: object,
        model_id: str,
        name: str,
        owned_by_identity_id: str,
        description: str | NotGiven = NOT_GIVEN,
        updated_at: Union[str, datetime] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> MlModelRole:
        """
        Args:
          config_override: # Optional Override for Model Configuration

          model_id: # Associated Model

          name: # Model Role Name

          owned_by_identity_id: # Model Role Owner

          description: # Description

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {"Accept": "application/json; charset=utf-8", **(extra_headers or {})}
        return await self._patch(
            f"/models/roles/{id}",
            body=await async_maybe_transform(
                {
                    "config_override": config_override,
                    "model_id": model_id,
                    "name": name,
                    "owned_by_identity_id": owned_by_identity_id,
                    "description": description,
                    "updated_at": updated_at,
                },
                role_update_partial_params.RoleUpdatePartialParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=MlModelRole,
        )


class RolesResourceWithRawResponse:
    def __init__(self, roles: RolesResource) -> None:
        self._roles = roles

        self.retrieve = to_raw_response_wrapper(
            roles.retrieve,
        )
        self.update = to_raw_response_wrapper(
            roles.update,
        )
        self.list = to_raw_response_wrapper(
            roles.list,
        )
        self.delete = to_raw_response_wrapper(
            roles.delete,
        )
        self.retrieve_schema = to_raw_response_wrapper(
            roles.retrieve_schema,
        )
        self.update_partial = to_raw_response_wrapper(
            roles.update_partial,
        )


class AsyncRolesResourceWithRawResponse:
    def __init__(self, roles: AsyncRolesResource) -> None:
        self._roles = roles

        self.retrieve = async_to_raw_response_wrapper(
            roles.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            roles.update,
        )
        self.list = async_to_raw_response_wrapper(
            roles.list,
        )
        self.delete = async_to_raw_response_wrapper(
            roles.delete,
        )
        self.retrieve_schema = async_to_raw_response_wrapper(
            roles.retrieve_schema,
        )
        self.update_partial = async_to_raw_response_wrapper(
            roles.update_partial,
        )


class RolesResourceWithStreamingResponse:
    def __init__(self, roles: RolesResource) -> None:
        self._roles = roles

        self.retrieve = to_streamed_response_wrapper(
            roles.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            roles.update,
        )
        self.list = to_streamed_response_wrapper(
            roles.list,
        )
        self.delete = to_streamed_response_wrapper(
            roles.delete,
        )
        self.retrieve_schema = to_streamed_response_wrapper(
            roles.retrieve_schema,
        )
        self.update_partial = to_streamed_response_wrapper(
            roles.update_partial,
        )


class AsyncRolesResourceWithStreamingResponse:
    def __init__(self, roles: AsyncRolesResource) -> None:
        self._roles = roles

        self.retrieve = async_to_streamed_response_wrapper(
            roles.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            roles.update,
        )
        self.list = async_to_streamed_response_wrapper(
            roles.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            roles.delete,
        )
        self.retrieve_schema = async_to_streamed_response_wrapper(
            roles.retrieve_schema,
        )
        self.update_partial = async_to_streamed_response_wrapper(
            roles.update_partial,
        )
