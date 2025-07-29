# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Literal

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
from ......types.worker.registry.quark.extractor import docling_extractor_run_params

__all__ = ["DoclingExtractorResource", "AsyncDoclingExtractorResource"]


class DoclingExtractorResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> DoclingExtractorResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/quarklabsai/quarkupy#accessing-raw-response-data-eg-headers
        """
        return DoclingExtractorResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> DoclingExtractorResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/quarklabsai/quarkupy#with_streaming_response
        """
        return DoclingExtractorResourceWithStreamingResponse(self)

    def run(
        self,
        *,
        ipc_dataset_id: str,
        lattice_id: str,
        opt_device: str | NotGiven = NOT_GIVEN,
        opt_do_cell_matching: bool | NotGiven = NOT_GIVEN,
        opt_do_ocr: bool | NotGiven = NOT_GIVEN,
        opt_do_table_structure: bool | NotGiven = NOT_GIVEN,
        opt_generate_page_images: bool | NotGiven = NOT_GIVEN,
        opt_generate_picture_images: bool | NotGiven = NOT_GIVEN,
        opt_image_resolution_scale: float | NotGiven = NOT_GIVEN,
        opt_input_file_types: List[Literal["AsciiDoc", "Docx", "HTML", "Image", "Markdown", "PDF", "PPTX"]]
        | NotGiven = NOT_GIVEN,
        opt_max_file_size: int | NotGiven = NOT_GIVEN,
        opt_max_pages: int | NotGiven = NOT_GIVEN,
        opt_output_type: Literal["DocTags", "HTML", "JSON", "Markdown", "Text"] | NotGiven = NOT_GIVEN,
        opt_use_gpu: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> QuarkHistoryItem:
        """
        Args:
          opt_device: Device to use for acceleration - options are CPU, CUDA, MPS, or AUTO

              Default is AUTO

          opt_do_cell_matching: Default is [false]

          opt_do_ocr: Whether to perform OCR

              Default is [true]

          opt_do_table_structure: Default is [false]

          opt_generate_page_images: Default: [true]

          opt_generate_picture_images: Default: [true]

          opt_image_resolution_scale: Default: 2.0

          opt_input_file_types: Limit input types

              Default is [Nome] - all supported

          opt_max_file_size: Limit the size of the file to extract from (in bytes)

              Default: [None]

          opt_max_pages: Limit the number of pages to extract

              Default is [None]

          opt_output_type: Supported output types for Docling

          opt_use_gpu: Best effort to use GPU

              Default is [true]

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "application/json; charset=utf-8", **(extra_headers or {})}
        return self._post(
            "/worker/registry/quark/extractor/docling_extractor/run",
            body=maybe_transform(
                {
                    "ipc_dataset_id": ipc_dataset_id,
                    "lattice_id": lattice_id,
                    "opt_device": opt_device,
                    "opt_do_cell_matching": opt_do_cell_matching,
                    "opt_do_ocr": opt_do_ocr,
                    "opt_do_table_structure": opt_do_table_structure,
                    "opt_generate_page_images": opt_generate_page_images,
                    "opt_generate_picture_images": opt_generate_picture_images,
                    "opt_image_resolution_scale": opt_image_resolution_scale,
                    "opt_input_file_types": opt_input_file_types,
                    "opt_max_file_size": opt_max_file_size,
                    "opt_max_pages": opt_max_pages,
                    "opt_output_type": opt_output_type,
                    "opt_use_gpu": opt_use_gpu,
                },
                docling_extractor_run_params.DoclingExtractorRunParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=QuarkHistoryItem,
        )


class AsyncDoclingExtractorResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncDoclingExtractorResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/quarklabsai/quarkupy#accessing-raw-response-data-eg-headers
        """
        return AsyncDoclingExtractorResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncDoclingExtractorResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/quarklabsai/quarkupy#with_streaming_response
        """
        return AsyncDoclingExtractorResourceWithStreamingResponse(self)

    async def run(
        self,
        *,
        ipc_dataset_id: str,
        lattice_id: str,
        opt_device: str | NotGiven = NOT_GIVEN,
        opt_do_cell_matching: bool | NotGiven = NOT_GIVEN,
        opt_do_ocr: bool | NotGiven = NOT_GIVEN,
        opt_do_table_structure: bool | NotGiven = NOT_GIVEN,
        opt_generate_page_images: bool | NotGiven = NOT_GIVEN,
        opt_generate_picture_images: bool | NotGiven = NOT_GIVEN,
        opt_image_resolution_scale: float | NotGiven = NOT_GIVEN,
        opt_input_file_types: List[Literal["AsciiDoc", "Docx", "HTML", "Image", "Markdown", "PDF", "PPTX"]]
        | NotGiven = NOT_GIVEN,
        opt_max_file_size: int | NotGiven = NOT_GIVEN,
        opt_max_pages: int | NotGiven = NOT_GIVEN,
        opt_output_type: Literal["DocTags", "HTML", "JSON", "Markdown", "Text"] | NotGiven = NOT_GIVEN,
        opt_use_gpu: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> QuarkHistoryItem:
        """
        Args:
          opt_device: Device to use for acceleration - options are CPU, CUDA, MPS, or AUTO

              Default is AUTO

          opt_do_cell_matching: Default is [false]

          opt_do_ocr: Whether to perform OCR

              Default is [true]

          opt_do_table_structure: Default is [false]

          opt_generate_page_images: Default: [true]

          opt_generate_picture_images: Default: [true]

          opt_image_resolution_scale: Default: 2.0

          opt_input_file_types: Limit input types

              Default is [Nome] - all supported

          opt_max_file_size: Limit the size of the file to extract from (in bytes)

              Default: [None]

          opt_max_pages: Limit the number of pages to extract

              Default is [None]

          opt_output_type: Supported output types for Docling

          opt_use_gpu: Best effort to use GPU

              Default is [true]

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "application/json; charset=utf-8", **(extra_headers or {})}
        return await self._post(
            "/worker/registry/quark/extractor/docling_extractor/run",
            body=await async_maybe_transform(
                {
                    "ipc_dataset_id": ipc_dataset_id,
                    "lattice_id": lattice_id,
                    "opt_device": opt_device,
                    "opt_do_cell_matching": opt_do_cell_matching,
                    "opt_do_ocr": opt_do_ocr,
                    "opt_do_table_structure": opt_do_table_structure,
                    "opt_generate_page_images": opt_generate_page_images,
                    "opt_generate_picture_images": opt_generate_picture_images,
                    "opt_image_resolution_scale": opt_image_resolution_scale,
                    "opt_input_file_types": opt_input_file_types,
                    "opt_max_file_size": opt_max_file_size,
                    "opt_max_pages": opt_max_pages,
                    "opt_output_type": opt_output_type,
                    "opt_use_gpu": opt_use_gpu,
                },
                docling_extractor_run_params.DoclingExtractorRunParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=QuarkHistoryItem,
        )


class DoclingExtractorResourceWithRawResponse:
    def __init__(self, docling_extractor: DoclingExtractorResource) -> None:
        self._docling_extractor = docling_extractor

        self.run = to_raw_response_wrapper(
            docling_extractor.run,
        )


class AsyncDoclingExtractorResourceWithRawResponse:
    def __init__(self, docling_extractor: AsyncDoclingExtractorResource) -> None:
        self._docling_extractor = docling_extractor

        self.run = async_to_raw_response_wrapper(
            docling_extractor.run,
        )


class DoclingExtractorResourceWithStreamingResponse:
    def __init__(self, docling_extractor: DoclingExtractorResource) -> None:
        self._docling_extractor = docling_extractor

        self.run = to_streamed_response_wrapper(
            docling_extractor.run,
        )


class AsyncDoclingExtractorResourceWithStreamingResponse:
    def __init__(self, docling_extractor: AsyncDoclingExtractorResource) -> None:
        self._docling_extractor = docling_extractor

        self.run = async_to_streamed_response_wrapper(
            docling_extractor.run,
        )
