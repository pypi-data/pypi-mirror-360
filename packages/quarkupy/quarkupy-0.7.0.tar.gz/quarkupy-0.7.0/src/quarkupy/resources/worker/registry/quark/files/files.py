# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from .opendal import (
    OpendalResource,
    AsyncOpendalResource,
    OpendalResourceWithRawResponse,
    AsyncOpendalResourceWithRawResponse,
    OpendalResourceWithStreamingResponse,
    AsyncOpendalResourceWithStreamingResponse,
)
from .s3_read_csv import (
    S3ReadCsvResource,
    AsyncS3ReadCsvResource,
    S3ReadCsvResourceWithRawResponse,
    AsyncS3ReadCsvResourceWithRawResponse,
    S3ReadCsvResourceWithStreamingResponse,
    AsyncS3ReadCsvResourceWithStreamingResponse,
)
from ......_compat import cached_property
from ......_resource import SyncAPIResource, AsyncAPIResource
from .s3_read_files_binary import (
    S3ReadFilesBinaryResource,
    AsyncS3ReadFilesBinaryResource,
    S3ReadFilesBinaryResourceWithRawResponse,
    AsyncS3ReadFilesBinaryResourceWithRawResponse,
    S3ReadFilesBinaryResourceWithStreamingResponse,
    AsyncS3ReadFilesBinaryResourceWithStreamingResponse,
)

__all__ = ["FilesResource", "AsyncFilesResource"]


class FilesResource(SyncAPIResource):
    @cached_property
    def s3_read_files_binary(self) -> S3ReadFilesBinaryResource:
        return S3ReadFilesBinaryResource(self._client)

    @cached_property
    def s3_read_csv(self) -> S3ReadCsvResource:
        return S3ReadCsvResource(self._client)

    @cached_property
    def opendal(self) -> OpendalResource:
        return OpendalResource(self._client)

    @cached_property
    def with_raw_response(self) -> FilesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/quarklabsai/quarkupy#accessing-raw-response-data-eg-headers
        """
        return FilesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> FilesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/quarklabsai/quarkupy#with_streaming_response
        """
        return FilesResourceWithStreamingResponse(self)


class AsyncFilesResource(AsyncAPIResource):
    @cached_property
    def s3_read_files_binary(self) -> AsyncS3ReadFilesBinaryResource:
        return AsyncS3ReadFilesBinaryResource(self._client)

    @cached_property
    def s3_read_csv(self) -> AsyncS3ReadCsvResource:
        return AsyncS3ReadCsvResource(self._client)

    @cached_property
    def opendal(self) -> AsyncOpendalResource:
        return AsyncOpendalResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncFilesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/quarklabsai/quarkupy#accessing-raw-response-data-eg-headers
        """
        return AsyncFilesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncFilesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/quarklabsai/quarkupy#with_streaming_response
        """
        return AsyncFilesResourceWithStreamingResponse(self)


class FilesResourceWithRawResponse:
    def __init__(self, files: FilesResource) -> None:
        self._files = files

    @cached_property
    def s3_read_files_binary(self) -> S3ReadFilesBinaryResourceWithRawResponse:
        return S3ReadFilesBinaryResourceWithRawResponse(self._files.s3_read_files_binary)

    @cached_property
    def s3_read_csv(self) -> S3ReadCsvResourceWithRawResponse:
        return S3ReadCsvResourceWithRawResponse(self._files.s3_read_csv)

    @cached_property
    def opendal(self) -> OpendalResourceWithRawResponse:
        return OpendalResourceWithRawResponse(self._files.opendal)


class AsyncFilesResourceWithRawResponse:
    def __init__(self, files: AsyncFilesResource) -> None:
        self._files = files

    @cached_property
    def s3_read_files_binary(self) -> AsyncS3ReadFilesBinaryResourceWithRawResponse:
        return AsyncS3ReadFilesBinaryResourceWithRawResponse(self._files.s3_read_files_binary)

    @cached_property
    def s3_read_csv(self) -> AsyncS3ReadCsvResourceWithRawResponse:
        return AsyncS3ReadCsvResourceWithRawResponse(self._files.s3_read_csv)

    @cached_property
    def opendal(self) -> AsyncOpendalResourceWithRawResponse:
        return AsyncOpendalResourceWithRawResponse(self._files.opendal)


class FilesResourceWithStreamingResponse:
    def __init__(self, files: FilesResource) -> None:
        self._files = files

    @cached_property
    def s3_read_files_binary(self) -> S3ReadFilesBinaryResourceWithStreamingResponse:
        return S3ReadFilesBinaryResourceWithStreamingResponse(self._files.s3_read_files_binary)

    @cached_property
    def s3_read_csv(self) -> S3ReadCsvResourceWithStreamingResponse:
        return S3ReadCsvResourceWithStreamingResponse(self._files.s3_read_csv)

    @cached_property
    def opendal(self) -> OpendalResourceWithStreamingResponse:
        return OpendalResourceWithStreamingResponse(self._files.opendal)


class AsyncFilesResourceWithStreamingResponse:
    def __init__(self, files: AsyncFilesResource) -> None:
        self._files = files

    @cached_property
    def s3_read_files_binary(self) -> AsyncS3ReadFilesBinaryResourceWithStreamingResponse:
        return AsyncS3ReadFilesBinaryResourceWithStreamingResponse(self._files.s3_read_files_binary)

    @cached_property
    def s3_read_csv(self) -> AsyncS3ReadCsvResourceWithStreamingResponse:
        return AsyncS3ReadCsvResourceWithStreamingResponse(self._files.s3_read_csv)

    @cached_property
    def opendal(self) -> AsyncOpendalResourceWithStreamingResponse:
        return AsyncOpendalResourceWithStreamingResponse(self._files.opendal)
