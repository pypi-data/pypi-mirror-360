# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from quarkupy import Quark, AsyncQuark
from tests.utils import assert_matches_type
from quarkupy.types.history import QuarkHistoryItem

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestSnowflakeRead:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_run(self, client: Quark) -> None:
        snowflake_read = client.worker.registry.quark.databases.snowflake_read.run(
            account="account",
            auth={
                "password": "password",
                "username": "username",
            },
            lattice_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            query="query",
        )
        assert_matches_type(QuarkHistoryItem, snowflake_read, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_run_with_all_params(self, client: Quark) -> None:
        snowflake_read = client.worker.registry.quark.databases.snowflake_read.run(
            account="account",
            auth={
                "password": "password",
                "username": "username",
            },
            lattice_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            query="query",
            opt_database="opt_database",
            opt_role="opt_role",
            opt_schema="opt_schema",
            opt_warehouse="opt_warehouse",
        )
        assert_matches_type(QuarkHistoryItem, snowflake_read, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_run(self, client: Quark) -> None:
        response = client.worker.registry.quark.databases.snowflake_read.with_raw_response.run(
            account="account",
            auth={
                "password": "password",
                "username": "username",
            },
            lattice_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            query="query",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        snowflake_read = response.parse()
        assert_matches_type(QuarkHistoryItem, snowflake_read, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_run(self, client: Quark) -> None:
        with client.worker.registry.quark.databases.snowflake_read.with_streaming_response.run(
            account="account",
            auth={
                "password": "password",
                "username": "username",
            },
            lattice_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            query="query",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            snowflake_read = response.parse()
            assert_matches_type(QuarkHistoryItem, snowflake_read, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncSnowflakeRead:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_run(self, async_client: AsyncQuark) -> None:
        snowflake_read = await async_client.worker.registry.quark.databases.snowflake_read.run(
            account="account",
            auth={
                "password": "password",
                "username": "username",
            },
            lattice_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            query="query",
        )
        assert_matches_type(QuarkHistoryItem, snowflake_read, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_run_with_all_params(self, async_client: AsyncQuark) -> None:
        snowflake_read = await async_client.worker.registry.quark.databases.snowflake_read.run(
            account="account",
            auth={
                "password": "password",
                "username": "username",
            },
            lattice_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            query="query",
            opt_database="opt_database",
            opt_role="opt_role",
            opt_schema="opt_schema",
            opt_warehouse="opt_warehouse",
        )
        assert_matches_type(QuarkHistoryItem, snowflake_read, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_run(self, async_client: AsyncQuark) -> None:
        response = await async_client.worker.registry.quark.databases.snowflake_read.with_raw_response.run(
            account="account",
            auth={
                "password": "password",
                "username": "username",
            },
            lattice_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            query="query",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        snowflake_read = await response.parse()
        assert_matches_type(QuarkHistoryItem, snowflake_read, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_run(self, async_client: AsyncQuark) -> None:
        async with async_client.worker.registry.quark.databases.snowflake_read.with_streaming_response.run(
            account="account",
            auth={
                "password": "password",
                "username": "username",
            },
            lattice_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            query="query",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            snowflake_read = await response.parse()
            assert_matches_type(QuarkHistoryItem, snowflake_read, path=["response"])

        assert cast(Any, response.is_closed) is True
