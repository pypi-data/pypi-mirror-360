# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from quarkupy import Quark, AsyncQuark
from tests.utils import assert_matches_type
from quarkupy.types.worker import (
    ManagementRetrieveResponse,
    ManagementRetrieveTokioResponse,
    ManagementRetrievePythonStatusResponse,
)
from quarkupy.types.context import SuccessResponseMessage
from quarkupy.types.admin.identity import IdentityModel

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestManagement:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve(self, client: Quark) -> None:
        management = client.worker.management.retrieve()
        assert_matches_type(ManagementRetrieveResponse, management, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_retrieve(self, client: Quark) -> None:
        response = client.worker.management.with_raw_response.retrieve()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        management = response.parse()
        assert_matches_type(ManagementRetrieveResponse, management, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_retrieve(self, client: Quark) -> None:
        with client.worker.management.with_streaming_response.retrieve() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            management = response.parse()
            assert_matches_type(ManagementRetrieveResponse, management, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_ping(self, client: Quark) -> None:
        management = client.worker.management.ping()
        assert_matches_type(SuccessResponseMessage, management, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_ping(self, client: Quark) -> None:
        response = client.worker.management.with_raw_response.ping()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        management = response.parse()
        assert_matches_type(SuccessResponseMessage, management, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_ping(self, client: Quark) -> None:
        with client.worker.management.with_streaming_response.ping() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            management = response.parse()
            assert_matches_type(SuccessResponseMessage, management, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve_auth_status(self, client: Quark) -> None:
        management = client.worker.management.retrieve_auth_status()
        assert_matches_type(IdentityModel, management, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_retrieve_auth_status(self, client: Quark) -> None:
        response = client.worker.management.with_raw_response.retrieve_auth_status()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        management = response.parse()
        assert_matches_type(IdentityModel, management, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_retrieve_auth_status(self, client: Quark) -> None:
        with client.worker.management.with_streaming_response.retrieve_auth_status() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            management = response.parse()
            assert_matches_type(IdentityModel, management, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve_python_status(self, client: Quark) -> None:
        management = client.worker.management.retrieve_python_status()
        assert_matches_type(ManagementRetrievePythonStatusResponse, management, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_retrieve_python_status(self, client: Quark) -> None:
        response = client.worker.management.with_raw_response.retrieve_python_status()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        management = response.parse()
        assert_matches_type(ManagementRetrievePythonStatusResponse, management, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_retrieve_python_status(self, client: Quark) -> None:
        with client.worker.management.with_streaming_response.retrieve_python_status() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            management = response.parse()
            assert_matches_type(ManagementRetrievePythonStatusResponse, management, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve_tokio(self, client: Quark) -> None:
        management = client.worker.management.retrieve_tokio()
        assert_matches_type(ManagementRetrieveTokioResponse, management, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve_tokio_with_all_params(self, client: Quark) -> None:
        management = client.worker.management.retrieve_tokio(
            with_dump=True,
        )
        assert_matches_type(ManagementRetrieveTokioResponse, management, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_retrieve_tokio(self, client: Quark) -> None:
        response = client.worker.management.with_raw_response.retrieve_tokio()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        management = response.parse()
        assert_matches_type(ManagementRetrieveTokioResponse, management, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_retrieve_tokio(self, client: Quark) -> None:
        with client.worker.management.with_streaming_response.retrieve_tokio() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            management = response.parse()
            assert_matches_type(ManagementRetrieveTokioResponse, management, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncManagement:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncQuark) -> None:
        management = await async_client.worker.management.retrieve()
        assert_matches_type(ManagementRetrieveResponse, management, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncQuark) -> None:
        response = await async_client.worker.management.with_raw_response.retrieve()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        management = await response.parse()
        assert_matches_type(ManagementRetrieveResponse, management, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncQuark) -> None:
        async with async_client.worker.management.with_streaming_response.retrieve() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            management = await response.parse()
            assert_matches_type(ManagementRetrieveResponse, management, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_ping(self, async_client: AsyncQuark) -> None:
        management = await async_client.worker.management.ping()
        assert_matches_type(SuccessResponseMessage, management, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_ping(self, async_client: AsyncQuark) -> None:
        response = await async_client.worker.management.with_raw_response.ping()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        management = await response.parse()
        assert_matches_type(SuccessResponseMessage, management, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_ping(self, async_client: AsyncQuark) -> None:
        async with async_client.worker.management.with_streaming_response.ping() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            management = await response.parse()
            assert_matches_type(SuccessResponseMessage, management, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve_auth_status(self, async_client: AsyncQuark) -> None:
        management = await async_client.worker.management.retrieve_auth_status()
        assert_matches_type(IdentityModel, management, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_retrieve_auth_status(self, async_client: AsyncQuark) -> None:
        response = await async_client.worker.management.with_raw_response.retrieve_auth_status()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        management = await response.parse()
        assert_matches_type(IdentityModel, management, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_retrieve_auth_status(self, async_client: AsyncQuark) -> None:
        async with async_client.worker.management.with_streaming_response.retrieve_auth_status() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            management = await response.parse()
            assert_matches_type(IdentityModel, management, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve_python_status(self, async_client: AsyncQuark) -> None:
        management = await async_client.worker.management.retrieve_python_status()
        assert_matches_type(ManagementRetrievePythonStatusResponse, management, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_retrieve_python_status(self, async_client: AsyncQuark) -> None:
        response = await async_client.worker.management.with_raw_response.retrieve_python_status()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        management = await response.parse()
        assert_matches_type(ManagementRetrievePythonStatusResponse, management, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_retrieve_python_status(self, async_client: AsyncQuark) -> None:
        async with async_client.worker.management.with_streaming_response.retrieve_python_status() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            management = await response.parse()
            assert_matches_type(ManagementRetrievePythonStatusResponse, management, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve_tokio(self, async_client: AsyncQuark) -> None:
        management = await async_client.worker.management.retrieve_tokio()
        assert_matches_type(ManagementRetrieveTokioResponse, management, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve_tokio_with_all_params(self, async_client: AsyncQuark) -> None:
        management = await async_client.worker.management.retrieve_tokio(
            with_dump=True,
        )
        assert_matches_type(ManagementRetrieveTokioResponse, management, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_retrieve_tokio(self, async_client: AsyncQuark) -> None:
        response = await async_client.worker.management.with_raw_response.retrieve_tokio()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        management = await response.parse()
        assert_matches_type(ManagementRetrieveTokioResponse, management, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_retrieve_tokio(self, async_client: AsyncQuark) -> None:
        async with async_client.worker.management.with_streaming_response.retrieve_tokio() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            management = await response.parse()
            assert_matches_type(ManagementRetrieveTokioResponse, management, path=["response"])

        assert cast(Any, response.is_closed) is True
