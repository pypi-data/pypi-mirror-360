# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from quarkupy import Quark, AsyncQuark
from tests.utils import assert_matches_type
from quarkupy.types.worker import RegistryListResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestRegistry:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_list(self, client: Quark) -> None:
        registry = client.worker.registry.list()
        assert_matches_type(RegistryListResponse, registry, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_list(self, client: Quark) -> None:
        response = client.worker.registry.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        registry = response.parse()
        assert_matches_type(RegistryListResponse, registry, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_list(self, client: Quark) -> None:
        with client.worker.registry.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            registry = response.parse()
            assert_matches_type(RegistryListResponse, registry, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncRegistry:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_list(self, async_client: AsyncQuark) -> None:
        registry = await async_client.worker.registry.list()
        assert_matches_type(RegistryListResponse, registry, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncQuark) -> None:
        response = await async_client.worker.registry.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        registry = await response.parse()
        assert_matches_type(RegistryListResponse, registry, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncQuark) -> None:
        async with async_client.worker.registry.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            registry = await response.parse()
            assert_matches_type(RegistryListResponse, registry, path=["response"])

        assert cast(Any, response.is_closed) is True
