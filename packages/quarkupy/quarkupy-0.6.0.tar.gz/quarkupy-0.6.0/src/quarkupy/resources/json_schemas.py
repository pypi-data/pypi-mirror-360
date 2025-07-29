# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from .._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options
from ..types.json_schema_list_response import JsonSchemaListResponse

__all__ = ["JsonSchemasResource", "AsyncJsonSchemasResource"]


class JsonSchemasResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> JsonSchemasResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/quarklabsai/quarkupy#accessing-raw-response-data-eg-headers
        """
        return JsonSchemasResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> JsonSchemasResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/quarklabsai/quarkupy#with_streaming_response
        """
        return JsonSchemasResourceWithStreamingResponse(self)

    def list(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> JsonSchemaListResponse:
        extra_headers = {"Accept": "application/json; charset=utf-8", **(extra_headers or {})}
        return self._get(
            "/json_schemas",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=JsonSchemaListResponse,
        )


class AsyncJsonSchemasResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncJsonSchemasResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/quarklabsai/quarkupy#accessing-raw-response-data-eg-headers
        """
        return AsyncJsonSchemasResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncJsonSchemasResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/quarklabsai/quarkupy#with_streaming_response
        """
        return AsyncJsonSchemasResourceWithStreamingResponse(self)

    async def list(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> JsonSchemaListResponse:
        extra_headers = {"Accept": "application/json; charset=utf-8", **(extra_headers or {})}
        return await self._get(
            "/json_schemas",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=JsonSchemaListResponse,
        )


class JsonSchemasResourceWithRawResponse:
    def __init__(self, json_schemas: JsonSchemasResource) -> None:
        self._json_schemas = json_schemas

        self.list = to_raw_response_wrapper(
            json_schemas.list,
        )


class AsyncJsonSchemasResourceWithRawResponse:
    def __init__(self, json_schemas: AsyncJsonSchemasResource) -> None:
        self._json_schemas = json_schemas

        self.list = async_to_raw_response_wrapper(
            json_schemas.list,
        )


class JsonSchemasResourceWithStreamingResponse:
    def __init__(self, json_schemas: JsonSchemasResource) -> None:
        self._json_schemas = json_schemas

        self.list = to_streamed_response_wrapper(
            json_schemas.list,
        )


class AsyncJsonSchemasResourceWithStreamingResponse:
    def __init__(self, json_schemas: AsyncJsonSchemasResource) -> None:
        self._json_schemas = json_schemas

        self.list = async_to_streamed_response_wrapper(
            json_schemas.list,
        )
