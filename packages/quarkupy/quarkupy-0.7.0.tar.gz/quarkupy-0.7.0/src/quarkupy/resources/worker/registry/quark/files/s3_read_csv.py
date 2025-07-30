# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ......_types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ......_utils import maybe_transform, async_maybe_transform
from ......_compat import cached_property
from ......_resource import SyncAPIResource, AsyncAPIResource
from ......_response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ......_base_client import make_request_options
from ......types.history.quark_history_item import QuarkHistoryItem
from ......types.worker.registry.quark.files import s3_read_csv_run_params

__all__ = ["S3ReadCsvResource", "AsyncS3ReadCsvResource"]


class S3ReadCsvResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> S3ReadCsvResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/quarklabsai/quarkupy#accessing-raw-response-data-eg-headers
        """
        return S3ReadCsvResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> S3ReadCsvResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/quarklabsai/quarkupy#with_streaming_response
        """
        return S3ReadCsvResourceWithStreamingResponse(self)

    def run(
        self,
        *,
        access_key_id: str,
        access_key_secret: str,
        lattice_id: str,
        url: str,
        opt_bucket: str | NotGiven = NOT_GIVEN,
        opt_enable_http: bool | NotGiven = NOT_GIVEN,
        opt_endpoint: str | NotGiven = NOT_GIVEN,
        opt_region: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> QuarkHistoryItem:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "application/json; charset=utf-8", **(extra_headers or {})}
        return self._post(
            "/worker/registry/quark/files/s3_read_csv/run",
            body=maybe_transform(
                {
                    "access_key_id": access_key_id,
                    "access_key_secret": access_key_secret,
                    "lattice_id": lattice_id,
                    "url": url,
                    "opt_bucket": opt_bucket,
                    "opt_enable_http": opt_enable_http,
                    "opt_endpoint": opt_endpoint,
                    "opt_region": opt_region,
                },
                s3_read_csv_run_params.S3ReadCsvRunParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=QuarkHistoryItem,
        )


class AsyncS3ReadCsvResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncS3ReadCsvResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/quarklabsai/quarkupy#accessing-raw-response-data-eg-headers
        """
        return AsyncS3ReadCsvResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncS3ReadCsvResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/quarklabsai/quarkupy#with_streaming_response
        """
        return AsyncS3ReadCsvResourceWithStreamingResponse(self)

    async def run(
        self,
        *,
        access_key_id: str,
        access_key_secret: str,
        lattice_id: str,
        url: str,
        opt_bucket: str | NotGiven = NOT_GIVEN,
        opt_enable_http: bool | NotGiven = NOT_GIVEN,
        opt_endpoint: str | NotGiven = NOT_GIVEN,
        opt_region: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> QuarkHistoryItem:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "application/json; charset=utf-8", **(extra_headers or {})}
        return await self._post(
            "/worker/registry/quark/files/s3_read_csv/run",
            body=await async_maybe_transform(
                {
                    "access_key_id": access_key_id,
                    "access_key_secret": access_key_secret,
                    "lattice_id": lattice_id,
                    "url": url,
                    "opt_bucket": opt_bucket,
                    "opt_enable_http": opt_enable_http,
                    "opt_endpoint": opt_endpoint,
                    "opt_region": opt_region,
                },
                s3_read_csv_run_params.S3ReadCsvRunParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=QuarkHistoryItem,
        )


class S3ReadCsvResourceWithRawResponse:
    def __init__(self, s3_read_csv: S3ReadCsvResource) -> None:
        self._s3_read_csv = s3_read_csv

        self.run = to_raw_response_wrapper(
            s3_read_csv.run,
        )


class AsyncS3ReadCsvResourceWithRawResponse:
    def __init__(self, s3_read_csv: AsyncS3ReadCsvResource) -> None:
        self._s3_read_csv = s3_read_csv

        self.run = async_to_raw_response_wrapper(
            s3_read_csv.run,
        )


class S3ReadCsvResourceWithStreamingResponse:
    def __init__(self, s3_read_csv: S3ReadCsvResource) -> None:
        self._s3_read_csv = s3_read_csv

        self.run = to_streamed_response_wrapper(
            s3_read_csv.run,
        )


class AsyncS3ReadCsvResourceWithStreamingResponse:
    def __init__(self, s3_read_csv: AsyncS3ReadCsvResource) -> None:
        self._s3_read_csv = s3_read_csv

        self.run = async_to_streamed_response_wrapper(
            s3_read_csv.run,
        )
