# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from quarkupy import Quark, AsyncQuark
from tests.utils import assert_matches_type
from quarkupy.types.history import QuarkHistoryItem

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestOpendal:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_run(self, client: Quark) -> None:
        opendal = client.worker.registry.quark.files.opendal.run(
            config={
                "bucket": "bucket",
                "type": "S3",
            },
            flow_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            source_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(QuarkHistoryItem, opendal, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_run_with_all_params(self, client: Quark) -> None:
        opendal = client.worker.registry.quark.files.opendal.run(
            config={
                "bucket": "bucket",
                "type": "S3",
                "access_key_id": "access_key_id",
                "allow_anonymous": True,
                "batch_max_operations": 0,
                "checksum_algorithm": "checksum_algorithm",
                "default_storage_class": "default_storage_class",
                "delete_max_size": 0,
                "disable_config_load": True,
                "disable_ec2_metadata": True,
                "disable_list_objects_v2": True,
                "disable_stat_with_override": True,
                "disable_write_with_if_match": True,
                "enable_request_payer": True,
                "enable_versioning": True,
                "enable_virtual_host_style": True,
                "enable_write_with_append": True,
                "endpoint": "endpoint",
                "external_id": "external_id",
                "region": "region",
                "role_arn": "role_arn",
                "role_session_name": "role_session_name",
                "root": "root",
                "secret_access_key": "secret_access_key",
                "server_side_encryption": "server_side_encryption",
                "server_side_encryption_aws_kms_key_id": "server_side_encryption_aws_kms_key_id",
                "server_side_encryption_customer_algorithm": "server_side_encryption_customer_algorithm",
                "server_side_encryption_customer_key": "server_side_encryption_customer_key",
                "server_side_encryption_customer_key_md5": "server_side_encryption_customer_key_md5",
                "session_token": "session_token",
            },
            flow_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            source_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            opt_paths=["string"],
            opt_recursive=True,
            opt_set_status="New",
        )
        assert_matches_type(QuarkHistoryItem, opendal, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_run(self, client: Quark) -> None:
        response = client.worker.registry.quark.files.opendal.with_raw_response.run(
            config={
                "bucket": "bucket",
                "type": "S3",
            },
            flow_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            source_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        opendal = response.parse()
        assert_matches_type(QuarkHistoryItem, opendal, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_run(self, client: Quark) -> None:
        with client.worker.registry.quark.files.opendal.with_streaming_response.run(
            config={
                "bucket": "bucket",
                "type": "S3",
            },
            flow_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            source_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            opendal = response.parse()
            assert_matches_type(QuarkHistoryItem, opendal, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_schema(self, client: Quark) -> None:
        opendal = client.worker.registry.quark.files.opendal.schema()
        assert_matches_type(object, opendal, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_schema(self, client: Quark) -> None:
        response = client.worker.registry.quark.files.opendal.with_raw_response.schema()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        opendal = response.parse()
        assert_matches_type(object, opendal, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_schema(self, client: Quark) -> None:
        with client.worker.registry.quark.files.opendal.with_streaming_response.schema() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            opendal = response.parse()
            assert_matches_type(object, opendal, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncOpendal:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_run(self, async_client: AsyncQuark) -> None:
        opendal = await async_client.worker.registry.quark.files.opendal.run(
            config={
                "bucket": "bucket",
                "type": "S3",
            },
            flow_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            source_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(QuarkHistoryItem, opendal, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_run_with_all_params(self, async_client: AsyncQuark) -> None:
        opendal = await async_client.worker.registry.quark.files.opendal.run(
            config={
                "bucket": "bucket",
                "type": "S3",
                "access_key_id": "access_key_id",
                "allow_anonymous": True,
                "batch_max_operations": 0,
                "checksum_algorithm": "checksum_algorithm",
                "default_storage_class": "default_storage_class",
                "delete_max_size": 0,
                "disable_config_load": True,
                "disable_ec2_metadata": True,
                "disable_list_objects_v2": True,
                "disable_stat_with_override": True,
                "disable_write_with_if_match": True,
                "enable_request_payer": True,
                "enable_versioning": True,
                "enable_virtual_host_style": True,
                "enable_write_with_append": True,
                "endpoint": "endpoint",
                "external_id": "external_id",
                "region": "region",
                "role_arn": "role_arn",
                "role_session_name": "role_session_name",
                "root": "root",
                "secret_access_key": "secret_access_key",
                "server_side_encryption": "server_side_encryption",
                "server_side_encryption_aws_kms_key_id": "server_side_encryption_aws_kms_key_id",
                "server_side_encryption_customer_algorithm": "server_side_encryption_customer_algorithm",
                "server_side_encryption_customer_key": "server_side_encryption_customer_key",
                "server_side_encryption_customer_key_md5": "server_side_encryption_customer_key_md5",
                "session_token": "session_token",
            },
            flow_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            source_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            opt_paths=["string"],
            opt_recursive=True,
            opt_set_status="New",
        )
        assert_matches_type(QuarkHistoryItem, opendal, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_run(self, async_client: AsyncQuark) -> None:
        response = await async_client.worker.registry.quark.files.opendal.with_raw_response.run(
            config={
                "bucket": "bucket",
                "type": "S3",
            },
            flow_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            source_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        opendal = await response.parse()
        assert_matches_type(QuarkHistoryItem, opendal, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_run(self, async_client: AsyncQuark) -> None:
        async with async_client.worker.registry.quark.files.opendal.with_streaming_response.run(
            config={
                "bucket": "bucket",
                "type": "S3",
            },
            flow_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            source_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            opendal = await response.parse()
            assert_matches_type(QuarkHistoryItem, opendal, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_schema(self, async_client: AsyncQuark) -> None:
        opendal = await async_client.worker.registry.quark.files.opendal.schema()
        assert_matches_type(object, opendal, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_schema(self, async_client: AsyncQuark) -> None:
        response = await async_client.worker.registry.quark.files.opendal.with_raw_response.schema()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        opendal = await response.parse()
        assert_matches_type(object, opendal, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_schema(self, async_client: AsyncQuark) -> None:
        async with async_client.worker.registry.quark.files.opendal.with_streaming_response.schema() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            opendal = await response.parse()
            assert_matches_type(object, opendal, path=["response"])

        assert cast(Any, response.is_closed) is True
