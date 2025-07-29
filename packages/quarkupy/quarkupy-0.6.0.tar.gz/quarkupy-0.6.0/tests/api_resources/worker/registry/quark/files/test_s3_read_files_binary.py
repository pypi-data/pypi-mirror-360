# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from quarkupy import Quark, AsyncQuark
from tests.utils import assert_matches_type
from quarkupy.types.history import QuarkHistoryItem

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestS3ReadFilesBinary:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_run(self, client: Quark) -> None:
        s3_read_files_binary = client.worker.registry.quark.files.s3_read_files_binary.run(
            access_key_id="access_key_id",
            access_key_secret="access_key_secret",
            lattice_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            url="url",
        )
        assert_matches_type(QuarkHistoryItem, s3_read_files_binary, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_run_with_all_params(self, client: Quark) -> None:
        s3_read_files_binary = client.worker.registry.quark.files.s3_read_files_binary.run(
            access_key_id="access_key_id",
            access_key_secret="access_key_secret",
            lattice_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            url="url",
            opt_bucket="opt_bucket",
            opt_enable_http=True,
            opt_endpoint="opt_endpoint",
            opt_region="opt_region",
        )
        assert_matches_type(QuarkHistoryItem, s3_read_files_binary, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_run(self, client: Quark) -> None:
        response = client.worker.registry.quark.files.s3_read_files_binary.with_raw_response.run(
            access_key_id="access_key_id",
            access_key_secret="access_key_secret",
            lattice_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            url="url",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        s3_read_files_binary = response.parse()
        assert_matches_type(QuarkHistoryItem, s3_read_files_binary, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_run(self, client: Quark) -> None:
        with client.worker.registry.quark.files.s3_read_files_binary.with_streaming_response.run(
            access_key_id="access_key_id",
            access_key_secret="access_key_secret",
            lattice_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            url="url",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            s3_read_files_binary = response.parse()
            assert_matches_type(QuarkHistoryItem, s3_read_files_binary, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncS3ReadFilesBinary:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_run(self, async_client: AsyncQuark) -> None:
        s3_read_files_binary = await async_client.worker.registry.quark.files.s3_read_files_binary.run(
            access_key_id="access_key_id",
            access_key_secret="access_key_secret",
            lattice_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            url="url",
        )
        assert_matches_type(QuarkHistoryItem, s3_read_files_binary, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_run_with_all_params(self, async_client: AsyncQuark) -> None:
        s3_read_files_binary = await async_client.worker.registry.quark.files.s3_read_files_binary.run(
            access_key_id="access_key_id",
            access_key_secret="access_key_secret",
            lattice_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            url="url",
            opt_bucket="opt_bucket",
            opt_enable_http=True,
            opt_endpoint="opt_endpoint",
            opt_region="opt_region",
        )
        assert_matches_type(QuarkHistoryItem, s3_read_files_binary, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_run(self, async_client: AsyncQuark) -> None:
        response = await async_client.worker.registry.quark.files.s3_read_files_binary.with_raw_response.run(
            access_key_id="access_key_id",
            access_key_secret="access_key_secret",
            lattice_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            url="url",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        s3_read_files_binary = await response.parse()
        assert_matches_type(QuarkHistoryItem, s3_read_files_binary, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_run(self, async_client: AsyncQuark) -> None:
        async with async_client.worker.registry.quark.files.s3_read_files_binary.with_streaming_response.run(
            access_key_id="access_key_id",
            access_key_secret="access_key_secret",
            lattice_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            url="url",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            s3_read_files_binary = await response.parse()
            assert_matches_type(QuarkHistoryItem, s3_read_files_binary, path=["response"])

        assert cast(Any, response.is_closed) is True
