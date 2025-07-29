# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from datetime import datetime
from typing_extensions import Literal

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
from ...types.context import ReferenceDepth, extractor_update_params, extractor_update_partial_params
from ...types.context.extractor import Extractor
from ...types.context.reference_depth import ReferenceDepth
from ...types.context.extractor_list_response import ExtractorListResponse
from ...types.context.success_response_message import SuccessResponseMessage

__all__ = ["ExtractorsResource", "AsyncExtractorsResource"]


class ExtractorsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ExtractorsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/quarklabsai/quarkupy#accessing-raw-response-data-eg-headers
        """
        return ExtractorsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ExtractorsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/quarklabsai/quarkupy#with_streaming_response
        """
        return ExtractorsResourceWithStreamingResponse(self)

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
    ) -> Extractor:
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
            f"/context/extractors/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Extractor,
        )

    def update(
        self,
        *,
        data_type: Literal["String", "Boolean", "Integer", "Float", "Rating", "Object", "Date", "Label"],
        model_role_id: str,
        name: str,
        owned_by_identity_id: str,
        reference_depth: ReferenceDepth,
        add_reason: bool | NotGiven = NOT_GIVEN,
        add_references: bool | NotGiven = NOT_GIVEN,
        config: object | NotGiven = NOT_GIVEN,
        description: str | NotGiven = NOT_GIVEN,
        examples: object | NotGiven = NOT_GIVEN,
        updated_at: Union[str, datetime] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Extractor:
        """
        Args:
          data_type: # Type of data to extract

          model_role_id: # Model Role to use for extraction

          name: # Extractor Name

          owned_by_identity_id: # Owner

          reference_depth: # Match Segments or Sentences

          add_reason: # Add reason for extracting this data

          add_references: # Add references to the extracted data

              Default is true

          description: # Extractor Description

              Note: the LLM uses this to perform the extraction, so be descriptive

          examples: # Examples of the data to extract

          updated_at: # Updated

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "application/json; charset=utf-8", **(extra_headers or {})}
        return self._put(
            "/context/extractors",
            body=maybe_transform(
                {
                    "data_type": data_type,
                    "model_role_id": model_role_id,
                    "name": name,
                    "owned_by_identity_id": owned_by_identity_id,
                    "reference_depth": reference_depth,
                    "add_reason": add_reason,
                    "add_references": add_references,
                    "config": config,
                    "description": description,
                    "examples": examples,
                    "updated_at": updated_at,
                },
                extractor_update_params.ExtractorUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Extractor,
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
    ) -> ExtractorListResponse:
        extra_headers = {"Accept": "application/json; charset=utf-8", **(extra_headers or {})}
        return self._get(
            "/context/extractors",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ExtractorListResponse,
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
            f"/context/extractors/{id}",
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
            "/context/extractors/schema",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    def update_partial(
        self,
        id: str,
        *,
        data_type: Literal["String", "Boolean", "Integer", "Float", "Rating", "Object", "Date", "Label"],
        model_role_id: str,
        name: str,
        owned_by_identity_id: str,
        reference_depth: ReferenceDepth,
        add_reason: bool | NotGiven = NOT_GIVEN,
        add_references: bool | NotGiven = NOT_GIVEN,
        config: object | NotGiven = NOT_GIVEN,
        description: str | NotGiven = NOT_GIVEN,
        examples: object | NotGiven = NOT_GIVEN,
        updated_at: Union[str, datetime] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Extractor:
        """
        Args:
          data_type: # Type of data to extract

          model_role_id: # Model Role to use for extraction

          name: # Extractor Name

          owned_by_identity_id: # Owner

          reference_depth: # Match Segments or Sentences

          add_reason: # Add reason for extracting this data

          add_references: # Add references to the extracted data

              Default is true

          description: # Extractor Description

              Note: the LLM uses this to perform the extraction, so be descriptive

          examples: # Examples of the data to extract

          updated_at: # Updated

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {"Accept": "application/json; charset=utf-8", **(extra_headers or {})}
        return self._patch(
            f"/context/extractors/{id}",
            body=maybe_transform(
                {
                    "data_type": data_type,
                    "model_role_id": model_role_id,
                    "name": name,
                    "owned_by_identity_id": owned_by_identity_id,
                    "reference_depth": reference_depth,
                    "add_reason": add_reason,
                    "add_references": add_references,
                    "config": config,
                    "description": description,
                    "examples": examples,
                    "updated_at": updated_at,
                },
                extractor_update_partial_params.ExtractorUpdatePartialParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Extractor,
        )


class AsyncExtractorsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncExtractorsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/quarklabsai/quarkupy#accessing-raw-response-data-eg-headers
        """
        return AsyncExtractorsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncExtractorsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/quarklabsai/quarkupy#with_streaming_response
        """
        return AsyncExtractorsResourceWithStreamingResponse(self)

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
    ) -> Extractor:
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
            f"/context/extractors/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Extractor,
        )

    async def update(
        self,
        *,
        data_type: Literal["String", "Boolean", "Integer", "Float", "Rating", "Object", "Date", "Label"],
        model_role_id: str,
        name: str,
        owned_by_identity_id: str,
        reference_depth: ReferenceDepth,
        add_reason: bool | NotGiven = NOT_GIVEN,
        add_references: bool | NotGiven = NOT_GIVEN,
        config: object | NotGiven = NOT_GIVEN,
        description: str | NotGiven = NOT_GIVEN,
        examples: object | NotGiven = NOT_GIVEN,
        updated_at: Union[str, datetime] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Extractor:
        """
        Args:
          data_type: # Type of data to extract

          model_role_id: # Model Role to use for extraction

          name: # Extractor Name

          owned_by_identity_id: # Owner

          reference_depth: # Match Segments or Sentences

          add_reason: # Add reason for extracting this data

          add_references: # Add references to the extracted data

              Default is true

          description: # Extractor Description

              Note: the LLM uses this to perform the extraction, so be descriptive

          examples: # Examples of the data to extract

          updated_at: # Updated

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "application/json; charset=utf-8", **(extra_headers or {})}
        return await self._put(
            "/context/extractors",
            body=await async_maybe_transform(
                {
                    "data_type": data_type,
                    "model_role_id": model_role_id,
                    "name": name,
                    "owned_by_identity_id": owned_by_identity_id,
                    "reference_depth": reference_depth,
                    "add_reason": add_reason,
                    "add_references": add_references,
                    "config": config,
                    "description": description,
                    "examples": examples,
                    "updated_at": updated_at,
                },
                extractor_update_params.ExtractorUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Extractor,
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
    ) -> ExtractorListResponse:
        extra_headers = {"Accept": "application/json; charset=utf-8", **(extra_headers or {})}
        return await self._get(
            "/context/extractors",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ExtractorListResponse,
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
            f"/context/extractors/{id}",
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
            "/context/extractors/schema",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    async def update_partial(
        self,
        id: str,
        *,
        data_type: Literal["String", "Boolean", "Integer", "Float", "Rating", "Object", "Date", "Label"],
        model_role_id: str,
        name: str,
        owned_by_identity_id: str,
        reference_depth: ReferenceDepth,
        add_reason: bool | NotGiven = NOT_GIVEN,
        add_references: bool | NotGiven = NOT_GIVEN,
        config: object | NotGiven = NOT_GIVEN,
        description: str | NotGiven = NOT_GIVEN,
        examples: object | NotGiven = NOT_GIVEN,
        updated_at: Union[str, datetime] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Extractor:
        """
        Args:
          data_type: # Type of data to extract

          model_role_id: # Model Role to use for extraction

          name: # Extractor Name

          owned_by_identity_id: # Owner

          reference_depth: # Match Segments or Sentences

          add_reason: # Add reason for extracting this data

          add_references: # Add references to the extracted data

              Default is true

          description: # Extractor Description

              Note: the LLM uses this to perform the extraction, so be descriptive

          examples: # Examples of the data to extract

          updated_at: # Updated

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {"Accept": "application/json; charset=utf-8", **(extra_headers or {})}
        return await self._patch(
            f"/context/extractors/{id}",
            body=await async_maybe_transform(
                {
                    "data_type": data_type,
                    "model_role_id": model_role_id,
                    "name": name,
                    "owned_by_identity_id": owned_by_identity_id,
                    "reference_depth": reference_depth,
                    "add_reason": add_reason,
                    "add_references": add_references,
                    "config": config,
                    "description": description,
                    "examples": examples,
                    "updated_at": updated_at,
                },
                extractor_update_partial_params.ExtractorUpdatePartialParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Extractor,
        )


class ExtractorsResourceWithRawResponse:
    def __init__(self, extractors: ExtractorsResource) -> None:
        self._extractors = extractors

        self.retrieve = to_raw_response_wrapper(
            extractors.retrieve,
        )
        self.update = to_raw_response_wrapper(
            extractors.update,
        )
        self.list = to_raw_response_wrapper(
            extractors.list,
        )
        self.delete = to_raw_response_wrapper(
            extractors.delete,
        )
        self.retrieve_schema = to_raw_response_wrapper(
            extractors.retrieve_schema,
        )
        self.update_partial = to_raw_response_wrapper(
            extractors.update_partial,
        )


class AsyncExtractorsResourceWithRawResponse:
    def __init__(self, extractors: AsyncExtractorsResource) -> None:
        self._extractors = extractors

        self.retrieve = async_to_raw_response_wrapper(
            extractors.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            extractors.update,
        )
        self.list = async_to_raw_response_wrapper(
            extractors.list,
        )
        self.delete = async_to_raw_response_wrapper(
            extractors.delete,
        )
        self.retrieve_schema = async_to_raw_response_wrapper(
            extractors.retrieve_schema,
        )
        self.update_partial = async_to_raw_response_wrapper(
            extractors.update_partial,
        )


class ExtractorsResourceWithStreamingResponse:
    def __init__(self, extractors: ExtractorsResource) -> None:
        self._extractors = extractors

        self.retrieve = to_streamed_response_wrapper(
            extractors.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            extractors.update,
        )
        self.list = to_streamed_response_wrapper(
            extractors.list,
        )
        self.delete = to_streamed_response_wrapper(
            extractors.delete,
        )
        self.retrieve_schema = to_streamed_response_wrapper(
            extractors.retrieve_schema,
        )
        self.update_partial = to_streamed_response_wrapper(
            extractors.update_partial,
        )


class AsyncExtractorsResourceWithStreamingResponse:
    def __init__(self, extractors: AsyncExtractorsResource) -> None:
        self._extractors = extractors

        self.retrieve = async_to_streamed_response_wrapper(
            extractors.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            extractors.update,
        )
        self.list = async_to_streamed_response_wrapper(
            extractors.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            extractors.delete,
        )
        self.retrieve_schema = async_to_streamed_response_wrapper(
            extractors.retrieve_schema,
        )
        self.update_partial = async_to_streamed_response_wrapper(
            extractors.update_partial,
        )
