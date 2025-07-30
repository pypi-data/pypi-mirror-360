# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..types import (
    dataset_retrieve_csv_params,
    dataset_retrieve_json_params,
    dataset_retrieve_arrow_params,
    dataset_retrieve_files_params,
    dataset_retrieve_chunks_params,
)
from .._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from .._utils import maybe_transform, async_maybe_transform
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    BinaryAPIResponse,
    AsyncBinaryAPIResponse,
    StreamedBinaryAPIResponse,
    AsyncStreamedBinaryAPIResponse,
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    to_custom_raw_response_wrapper,
    async_to_streamed_response_wrapper,
    to_custom_streamed_response_wrapper,
    async_to_custom_raw_response_wrapper,
    async_to_custom_streamed_response_wrapper,
)
from .._base_client import make_request_options
from ..types.data_set_info import DataSetInfo
from ..types.dataset_list_response import DatasetListResponse

__all__ = ["DatasetResource", "AsyncDatasetResource"]


class DatasetResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> DatasetResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/quarklabsai/quarkupy#accessing-raw-response-data-eg-headers
        """
        return DatasetResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> DatasetResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/quarklabsai/quarkupy#with_streaming_response
        """
        return DatasetResourceWithStreamingResponse(self)

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
    ) -> DataSetInfo:
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
            f"/dataset/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DataSetInfo,
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
    ) -> DatasetListResponse:
        extra_headers = {"Accept": "application/json; charset=utf-8", **(extra_headers or {})}
        return self._get(
            "/dataset",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DatasetListResponse,
        )

    def retrieve_arrow(
        self,
        id: str,
        *,
        _limit: int | NotGiven = NOT_GIVEN,
        _offset: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> BinaryAPIResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {"Accept": "application/x-apache-arrow-stream", **(extra_headers or {})}
        return self._get(
            f"/dataset/{id}/arrow",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "_limit": _limit,
                        "_offset": _offset,
                    },
                    dataset_retrieve_arrow_params.DatasetRetrieveArrowParams,
                ),
            ),
            cast_to=BinaryAPIResponse,
        )

    def retrieve_chunks(
        self,
        file_id: str,
        *,
        id: str,
        _limit: int | NotGiven = NOT_GIVEN,
        _offset: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> BinaryAPIResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        if not file_id:
            raise ValueError(f"Expected a non-empty value for `file_id` but received {file_id!r}")
        extra_headers = {"Accept": "application/x-apache-arrow-stream", **(extra_headers or {})}
        return self._get(
            f"/dataset/{id}/{file_id}/chunks",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "_limit": _limit,
                        "_offset": _offset,
                    },
                    dataset_retrieve_chunks_params.DatasetRetrieveChunksParams,
                ),
            ),
            cast_to=BinaryAPIResponse,
        )

    def retrieve_csv(
        self,
        id: str,
        *,
        limit: int | NotGiven = NOT_GIVEN,
        offset: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> str:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {"Accept": "text/csv", **(extra_headers or {})}
        return self._get(
            f"/dataset/{id}/csv",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "limit": limit,
                        "offset": offset,
                    },
                    dataset_retrieve_csv_params.DatasetRetrieveCsvParams,
                ),
            ),
            cast_to=str,
        )

    def retrieve_files(
        self,
        id: str,
        *,
        _limit: int | NotGiven = NOT_GIVEN,
        _offset: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> BinaryAPIResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {"Accept": "application/x-apache-arrow-stream", **(extra_headers or {})}
        return self._get(
            f"/dataset/{id}/files",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "_limit": _limit,
                        "_offset": _offset,
                    },
                    dataset_retrieve_files_params.DatasetRetrieveFilesParams,
                ),
            ),
            cast_to=BinaryAPIResponse,
        )

    def retrieve_json(
        self,
        id: str,
        *,
        max_cell_size: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> str:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._get(
            f"/dataset/{id}/json",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"max_cell_size": max_cell_size}, dataset_retrieve_json_params.DatasetRetrieveJsonParams
                ),
            ),
            cast_to=str,
        )


class AsyncDatasetResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncDatasetResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/quarklabsai/quarkupy#accessing-raw-response-data-eg-headers
        """
        return AsyncDatasetResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncDatasetResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/quarklabsai/quarkupy#with_streaming_response
        """
        return AsyncDatasetResourceWithStreamingResponse(self)

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
    ) -> DataSetInfo:
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
            f"/dataset/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DataSetInfo,
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
    ) -> DatasetListResponse:
        extra_headers = {"Accept": "application/json; charset=utf-8", **(extra_headers or {})}
        return await self._get(
            "/dataset",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DatasetListResponse,
        )

    async def retrieve_arrow(
        self,
        id: str,
        *,
        _limit: int | NotGiven = NOT_GIVEN,
        _offset: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AsyncBinaryAPIResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {"Accept": "application/x-apache-arrow-stream", **(extra_headers or {})}
        return await self._get(
            f"/dataset/{id}/arrow",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "_limit": _limit,
                        "_offset": _offset,
                    },
                    dataset_retrieve_arrow_params.DatasetRetrieveArrowParams,
                ),
            ),
            cast_to=AsyncBinaryAPIResponse,
        )

    async def retrieve_chunks(
        self,
        file_id: str,
        *,
        id: str,
        _limit: int | NotGiven = NOT_GIVEN,
        _offset: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AsyncBinaryAPIResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        if not file_id:
            raise ValueError(f"Expected a non-empty value for `file_id` but received {file_id!r}")
        extra_headers = {"Accept": "application/x-apache-arrow-stream", **(extra_headers or {})}
        return await self._get(
            f"/dataset/{id}/{file_id}/chunks",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "_limit": _limit,
                        "_offset": _offset,
                    },
                    dataset_retrieve_chunks_params.DatasetRetrieveChunksParams,
                ),
            ),
            cast_to=AsyncBinaryAPIResponse,
        )

    async def retrieve_csv(
        self,
        id: str,
        *,
        limit: int | NotGiven = NOT_GIVEN,
        offset: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> str:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {"Accept": "text/csv", **(extra_headers or {})}
        return await self._get(
            f"/dataset/{id}/csv",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "limit": limit,
                        "offset": offset,
                    },
                    dataset_retrieve_csv_params.DatasetRetrieveCsvParams,
                ),
            ),
            cast_to=str,
        )

    async def retrieve_files(
        self,
        id: str,
        *,
        _limit: int | NotGiven = NOT_GIVEN,
        _offset: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AsyncBinaryAPIResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {"Accept": "application/x-apache-arrow-stream", **(extra_headers or {})}
        return await self._get(
            f"/dataset/{id}/files",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "_limit": _limit,
                        "_offset": _offset,
                    },
                    dataset_retrieve_files_params.DatasetRetrieveFilesParams,
                ),
            ),
            cast_to=AsyncBinaryAPIResponse,
        )

    async def retrieve_json(
        self,
        id: str,
        *,
        max_cell_size: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> str:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._get(
            f"/dataset/{id}/json",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"max_cell_size": max_cell_size}, dataset_retrieve_json_params.DatasetRetrieveJsonParams
                ),
            ),
            cast_to=str,
        )


class DatasetResourceWithRawResponse:
    def __init__(self, dataset: DatasetResource) -> None:
        self._dataset = dataset

        self.retrieve = to_raw_response_wrapper(
            dataset.retrieve,
        )
        self.list = to_raw_response_wrapper(
            dataset.list,
        )
        self.retrieve_arrow = to_custom_raw_response_wrapper(
            dataset.retrieve_arrow,
            BinaryAPIResponse,
        )
        self.retrieve_chunks = to_custom_raw_response_wrapper(
            dataset.retrieve_chunks,
            BinaryAPIResponse,
        )
        self.retrieve_csv = to_raw_response_wrapper(
            dataset.retrieve_csv,
        )
        self.retrieve_files = to_custom_raw_response_wrapper(
            dataset.retrieve_files,
            BinaryAPIResponse,
        )
        self.retrieve_json = to_raw_response_wrapper(
            dataset.retrieve_json,
        )


class AsyncDatasetResourceWithRawResponse:
    def __init__(self, dataset: AsyncDatasetResource) -> None:
        self._dataset = dataset

        self.retrieve = async_to_raw_response_wrapper(
            dataset.retrieve,
        )
        self.list = async_to_raw_response_wrapper(
            dataset.list,
        )
        self.retrieve_arrow = async_to_custom_raw_response_wrapper(
            dataset.retrieve_arrow,
            AsyncBinaryAPIResponse,
        )
        self.retrieve_chunks = async_to_custom_raw_response_wrapper(
            dataset.retrieve_chunks,
            AsyncBinaryAPIResponse,
        )
        self.retrieve_csv = async_to_raw_response_wrapper(
            dataset.retrieve_csv,
        )
        self.retrieve_files = async_to_custom_raw_response_wrapper(
            dataset.retrieve_files,
            AsyncBinaryAPIResponse,
        )
        self.retrieve_json = async_to_raw_response_wrapper(
            dataset.retrieve_json,
        )


class DatasetResourceWithStreamingResponse:
    def __init__(self, dataset: DatasetResource) -> None:
        self._dataset = dataset

        self.retrieve = to_streamed_response_wrapper(
            dataset.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            dataset.list,
        )
        self.retrieve_arrow = to_custom_streamed_response_wrapper(
            dataset.retrieve_arrow,
            StreamedBinaryAPIResponse,
        )
        self.retrieve_chunks = to_custom_streamed_response_wrapper(
            dataset.retrieve_chunks,
            StreamedBinaryAPIResponse,
        )
        self.retrieve_csv = to_streamed_response_wrapper(
            dataset.retrieve_csv,
        )
        self.retrieve_files = to_custom_streamed_response_wrapper(
            dataset.retrieve_files,
            StreamedBinaryAPIResponse,
        )
        self.retrieve_json = to_streamed_response_wrapper(
            dataset.retrieve_json,
        )


class AsyncDatasetResourceWithStreamingResponse:
    def __init__(self, dataset: AsyncDatasetResource) -> None:
        self._dataset = dataset

        self.retrieve = async_to_streamed_response_wrapper(
            dataset.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            dataset.list,
        )
        self.retrieve_arrow = async_to_custom_streamed_response_wrapper(
            dataset.retrieve_arrow,
            AsyncStreamedBinaryAPIResponse,
        )
        self.retrieve_chunks = async_to_custom_streamed_response_wrapper(
            dataset.retrieve_chunks,
            AsyncStreamedBinaryAPIResponse,
        )
        self.retrieve_csv = async_to_streamed_response_wrapper(
            dataset.retrieve_csv,
        )
        self.retrieve_files = async_to_custom_streamed_response_wrapper(
            dataset.retrieve_files,
            AsyncStreamedBinaryAPIResponse,
        )
        self.retrieve_json = async_to_streamed_response_wrapper(
            dataset.retrieve_json,
        )
