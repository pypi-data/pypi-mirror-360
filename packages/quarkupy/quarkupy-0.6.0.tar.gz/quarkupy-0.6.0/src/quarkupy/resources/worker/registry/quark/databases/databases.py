# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from ......_compat import cached_property
from ......_resource import SyncAPIResource, AsyncAPIResource
from .snowflake_read import (
    SnowflakeReadResource,
    AsyncSnowflakeReadResource,
    SnowflakeReadResourceWithRawResponse,
    AsyncSnowflakeReadResourceWithRawResponse,
    SnowflakeReadResourceWithStreamingResponse,
    AsyncSnowflakeReadResourceWithStreamingResponse,
)

__all__ = ["DatabasesResource", "AsyncDatabasesResource"]


class DatabasesResource(SyncAPIResource):
    @cached_property
    def snowflake_read(self) -> SnowflakeReadResource:
        return SnowflakeReadResource(self._client)

    @cached_property
    def with_raw_response(self) -> DatabasesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/quarklabsai/quarkupy#accessing-raw-response-data-eg-headers
        """
        return DatabasesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> DatabasesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/quarklabsai/quarkupy#with_streaming_response
        """
        return DatabasesResourceWithStreamingResponse(self)


class AsyncDatabasesResource(AsyncAPIResource):
    @cached_property
    def snowflake_read(self) -> AsyncSnowflakeReadResource:
        return AsyncSnowflakeReadResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncDatabasesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/quarklabsai/quarkupy#accessing-raw-response-data-eg-headers
        """
        return AsyncDatabasesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncDatabasesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/quarklabsai/quarkupy#with_streaming_response
        """
        return AsyncDatabasesResourceWithStreamingResponse(self)


class DatabasesResourceWithRawResponse:
    def __init__(self, databases: DatabasesResource) -> None:
        self._databases = databases

    @cached_property
    def snowflake_read(self) -> SnowflakeReadResourceWithRawResponse:
        return SnowflakeReadResourceWithRawResponse(self._databases.snowflake_read)


class AsyncDatabasesResourceWithRawResponse:
    def __init__(self, databases: AsyncDatabasesResource) -> None:
        self._databases = databases

    @cached_property
    def snowflake_read(self) -> AsyncSnowflakeReadResourceWithRawResponse:
        return AsyncSnowflakeReadResourceWithRawResponse(self._databases.snowflake_read)


class DatabasesResourceWithStreamingResponse:
    def __init__(self, databases: DatabasesResource) -> None:
        self._databases = databases

    @cached_property
    def snowflake_read(self) -> SnowflakeReadResourceWithStreamingResponse:
        return SnowflakeReadResourceWithStreamingResponse(self._databases.snowflake_read)


class AsyncDatabasesResourceWithStreamingResponse:
    def __init__(self, databases: AsyncDatabasesResource) -> None:
        self._databases = databases

    @cached_property
    def snowflake_read(self) -> AsyncSnowflakeReadResourceWithStreamingResponse:
        return AsyncSnowflakeReadResourceWithStreamingResponse(self._databases.snowflake_read)
