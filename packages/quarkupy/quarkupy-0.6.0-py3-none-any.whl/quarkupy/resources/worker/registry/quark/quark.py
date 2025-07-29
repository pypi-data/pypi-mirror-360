# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from .ai.ai import (
    AIResource,
    AsyncAIResource,
    AIResourceWithRawResponse,
    AsyncAIResourceWithRawResponse,
    AIResourceWithStreamingResponse,
    AsyncAIResourceWithStreamingResponse,
)
from ....._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ....._compat import cached_property
from .files.files import (
    FilesResource,
    AsyncFilesResource,
    FilesResourceWithRawResponse,
    AsyncFilesResourceWithRawResponse,
    FilesResourceWithStreamingResponse,
    AsyncFilesResourceWithStreamingResponse,
)
from .other.other import (
    OtherResource,
    AsyncOtherResource,
    OtherResourceWithRawResponse,
    AsyncOtherResourceWithRawResponse,
    OtherResourceWithStreamingResponse,
    AsyncOtherResourceWithStreamingResponse,
)
from ....._resource import SyncAPIResource, AsyncAPIResource
from ....._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .vector.vector import (
    VectorResource,
    AsyncVectorResource,
    VectorResourceWithRawResponse,
    AsyncVectorResourceWithRawResponse,
    VectorResourceWithStreamingResponse,
    AsyncVectorResourceWithStreamingResponse,
)
from ....._base_client import make_request_options
from .databases.databases import (
    DatabasesResource,
    AsyncDatabasesResource,
    DatabasesResourceWithRawResponse,
    AsyncDatabasesResourceWithRawResponse,
    DatabasesResourceWithStreamingResponse,
    AsyncDatabasesResourceWithStreamingResponse,
)
from .extractor.extractor import (
    ExtractorResource,
    AsyncExtractorResource,
    ExtractorResourceWithRawResponse,
    AsyncExtractorResourceWithRawResponse,
    ExtractorResourceWithStreamingResponse,
    AsyncExtractorResourceWithStreamingResponse,
)
from .transformer.transformer import (
    TransformerResource,
    AsyncTransformerResource,
    TransformerResourceWithRawResponse,
    AsyncTransformerResourceWithRawResponse,
    TransformerResourceWithStreamingResponse,
    AsyncTransformerResourceWithStreamingResponse,
)
from .....types.worker.registry.quark_registry_item import QuarkRegistryItem

__all__ = ["QuarkResource", "AsyncQuarkResource"]


class QuarkResource(SyncAPIResource):
    @cached_property
    def files(self) -> FilesResource:
        return FilesResource(self._client)

    @cached_property
    def extractor(self) -> ExtractorResource:
        return ExtractorResource(self._client)

    @cached_property
    def ai(self) -> AIResource:
        return AIResource(self._client)

    @cached_property
    def transformer(self) -> TransformerResource:
        return TransformerResource(self._client)

    @cached_property
    def databases(self) -> DatabasesResource:
        return DatabasesResource(self._client)

    @cached_property
    def vector(self) -> VectorResource:
        return VectorResource(self._client)

    @cached_property
    def other(self) -> OtherResource:
        return OtherResource(self._client)

    @cached_property
    def with_raw_response(self) -> QuarkResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/quarklabsai/quarkupy#accessing-raw-response-data-eg-headers
        """
        return QuarkResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> QuarkResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/quarklabsai/quarkupy#with_streaming_response
        """
        return QuarkResourceWithStreamingResponse(self)

    def retrieve(
        self,
        name: str,
        *,
        cat: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> QuarkRegistryItem:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not cat:
            raise ValueError(f"Expected a non-empty value for `cat` but received {cat!r}")
        if not name:
            raise ValueError(f"Expected a non-empty value for `name` but received {name!r}")
        extra_headers = {"Accept": "application/json; charset=utf-8", **(extra_headers or {})}
        return self._get(
            f"/worker/registry/quark/{cat}/{name}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=QuarkRegistryItem,
        )


class AsyncQuarkResource(AsyncAPIResource):
    @cached_property
    def files(self) -> AsyncFilesResource:
        return AsyncFilesResource(self._client)

    @cached_property
    def extractor(self) -> AsyncExtractorResource:
        return AsyncExtractorResource(self._client)

    @cached_property
    def ai(self) -> AsyncAIResource:
        return AsyncAIResource(self._client)

    @cached_property
    def transformer(self) -> AsyncTransformerResource:
        return AsyncTransformerResource(self._client)

    @cached_property
    def databases(self) -> AsyncDatabasesResource:
        return AsyncDatabasesResource(self._client)

    @cached_property
    def vector(self) -> AsyncVectorResource:
        return AsyncVectorResource(self._client)

    @cached_property
    def other(self) -> AsyncOtherResource:
        return AsyncOtherResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncQuarkResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/quarklabsai/quarkupy#accessing-raw-response-data-eg-headers
        """
        return AsyncQuarkResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncQuarkResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/quarklabsai/quarkupy#with_streaming_response
        """
        return AsyncQuarkResourceWithStreamingResponse(self)

    async def retrieve(
        self,
        name: str,
        *,
        cat: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> QuarkRegistryItem:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not cat:
            raise ValueError(f"Expected a non-empty value for `cat` but received {cat!r}")
        if not name:
            raise ValueError(f"Expected a non-empty value for `name` but received {name!r}")
        extra_headers = {"Accept": "application/json; charset=utf-8", **(extra_headers or {})}
        return await self._get(
            f"/worker/registry/quark/{cat}/{name}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=QuarkRegistryItem,
        )


class QuarkResourceWithRawResponse:
    def __init__(self, quark: QuarkResource) -> None:
        self._quark = quark

        self.retrieve = to_raw_response_wrapper(
            quark.retrieve,
        )

    @cached_property
    def files(self) -> FilesResourceWithRawResponse:
        return FilesResourceWithRawResponse(self._quark.files)

    @cached_property
    def extractor(self) -> ExtractorResourceWithRawResponse:
        return ExtractorResourceWithRawResponse(self._quark.extractor)

    @cached_property
    def ai(self) -> AIResourceWithRawResponse:
        return AIResourceWithRawResponse(self._quark.ai)

    @cached_property
    def transformer(self) -> TransformerResourceWithRawResponse:
        return TransformerResourceWithRawResponse(self._quark.transformer)

    @cached_property
    def databases(self) -> DatabasesResourceWithRawResponse:
        return DatabasesResourceWithRawResponse(self._quark.databases)

    @cached_property
    def vector(self) -> VectorResourceWithRawResponse:
        return VectorResourceWithRawResponse(self._quark.vector)

    @cached_property
    def other(self) -> OtherResourceWithRawResponse:
        return OtherResourceWithRawResponse(self._quark.other)


class AsyncQuarkResourceWithRawResponse:
    def __init__(self, quark: AsyncQuarkResource) -> None:
        self._quark = quark

        self.retrieve = async_to_raw_response_wrapper(
            quark.retrieve,
        )

    @cached_property
    def files(self) -> AsyncFilesResourceWithRawResponse:
        return AsyncFilesResourceWithRawResponse(self._quark.files)

    @cached_property
    def extractor(self) -> AsyncExtractorResourceWithRawResponse:
        return AsyncExtractorResourceWithRawResponse(self._quark.extractor)

    @cached_property
    def ai(self) -> AsyncAIResourceWithRawResponse:
        return AsyncAIResourceWithRawResponse(self._quark.ai)

    @cached_property
    def transformer(self) -> AsyncTransformerResourceWithRawResponse:
        return AsyncTransformerResourceWithRawResponse(self._quark.transformer)

    @cached_property
    def databases(self) -> AsyncDatabasesResourceWithRawResponse:
        return AsyncDatabasesResourceWithRawResponse(self._quark.databases)

    @cached_property
    def vector(self) -> AsyncVectorResourceWithRawResponse:
        return AsyncVectorResourceWithRawResponse(self._quark.vector)

    @cached_property
    def other(self) -> AsyncOtherResourceWithRawResponse:
        return AsyncOtherResourceWithRawResponse(self._quark.other)


class QuarkResourceWithStreamingResponse:
    def __init__(self, quark: QuarkResource) -> None:
        self._quark = quark

        self.retrieve = to_streamed_response_wrapper(
            quark.retrieve,
        )

    @cached_property
    def files(self) -> FilesResourceWithStreamingResponse:
        return FilesResourceWithStreamingResponse(self._quark.files)

    @cached_property
    def extractor(self) -> ExtractorResourceWithStreamingResponse:
        return ExtractorResourceWithStreamingResponse(self._quark.extractor)

    @cached_property
    def ai(self) -> AIResourceWithStreamingResponse:
        return AIResourceWithStreamingResponse(self._quark.ai)

    @cached_property
    def transformer(self) -> TransformerResourceWithStreamingResponse:
        return TransformerResourceWithStreamingResponse(self._quark.transformer)

    @cached_property
    def databases(self) -> DatabasesResourceWithStreamingResponse:
        return DatabasesResourceWithStreamingResponse(self._quark.databases)

    @cached_property
    def vector(self) -> VectorResourceWithStreamingResponse:
        return VectorResourceWithStreamingResponse(self._quark.vector)

    @cached_property
    def other(self) -> OtherResourceWithStreamingResponse:
        return OtherResourceWithStreamingResponse(self._quark.other)


class AsyncQuarkResourceWithStreamingResponse:
    def __init__(self, quark: AsyncQuarkResource) -> None:
        self._quark = quark

        self.retrieve = async_to_streamed_response_wrapper(
            quark.retrieve,
        )

    @cached_property
    def files(self) -> AsyncFilesResourceWithStreamingResponse:
        return AsyncFilesResourceWithStreamingResponse(self._quark.files)

    @cached_property
    def extractor(self) -> AsyncExtractorResourceWithStreamingResponse:
        return AsyncExtractorResourceWithStreamingResponse(self._quark.extractor)

    @cached_property
    def ai(self) -> AsyncAIResourceWithStreamingResponse:
        return AsyncAIResourceWithStreamingResponse(self._quark.ai)

    @cached_property
    def transformer(self) -> AsyncTransformerResourceWithStreamingResponse:
        return AsyncTransformerResourceWithStreamingResponse(self._quark.transformer)

    @cached_property
    def databases(self) -> AsyncDatabasesResourceWithStreamingResponse:
        return AsyncDatabasesResourceWithStreamingResponse(self._quark.databases)

    @cached_property
    def vector(self) -> AsyncVectorResourceWithStreamingResponse:
        return AsyncVectorResourceWithStreamingResponse(self._quark.vector)

    @cached_property
    def other(self) -> AsyncOtherResourceWithStreamingResponse:
        return AsyncOtherResourceWithStreamingResponse(self._quark.other)
