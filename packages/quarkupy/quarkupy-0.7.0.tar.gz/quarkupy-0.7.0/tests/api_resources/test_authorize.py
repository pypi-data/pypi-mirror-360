# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from quarkupy import Quark, AsyncQuark

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestAuthorize:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism doesn't properly handle redirects")
    @parametrize
    def test_method_retrieve(self, client: Quark) -> None:
        authorize = client.authorize.retrieve(
            code="code",
        )
        assert authorize is None

    @pytest.mark.skip(reason="Prism doesn't properly handle redirects")
    @parametrize
    def test_method_retrieve_with_all_params(self, client: Quark) -> None:
        authorize = client.authorize.retrieve(
            code="code",
            _state="_state",
        )
        assert authorize is None

    @pytest.mark.skip(reason="Prism doesn't properly handle redirects")
    @parametrize
    def test_raw_response_retrieve(self, client: Quark) -> None:
        response = client.authorize.with_raw_response.retrieve(
            code="code",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        authorize = response.parse()
        assert authorize is None

    @pytest.mark.skip(reason="Prism doesn't properly handle redirects")
    @parametrize
    def test_streaming_response_retrieve(self, client: Quark) -> None:
        with client.authorize.with_streaming_response.retrieve(
            code="code",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            authorize = response.parse()
            assert authorize is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism doesn't properly handle redirects")
    @parametrize
    def test_method_logout(self, client: Quark) -> None:
        authorize = client.authorize.logout()
        assert authorize is None

    @pytest.mark.skip(reason="Prism doesn't properly handle redirects")
    @parametrize
    def test_raw_response_logout(self, client: Quark) -> None:
        response = client.authorize.with_raw_response.logout()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        authorize = response.parse()
        assert authorize is None

    @pytest.mark.skip(reason="Prism doesn't properly handle redirects")
    @parametrize
    def test_streaming_response_logout(self, client: Quark) -> None:
        with client.authorize.with_streaming_response.logout() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            authorize = response.parse()
            assert authorize is None

        assert cast(Any, response.is_closed) is True


class TestAsyncAuthorize:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism doesn't properly handle redirects")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncQuark) -> None:
        authorize = await async_client.authorize.retrieve(
            code="code",
        )
        assert authorize is None

    @pytest.mark.skip(reason="Prism doesn't properly handle redirects")
    @parametrize
    async def test_method_retrieve_with_all_params(self, async_client: AsyncQuark) -> None:
        authorize = await async_client.authorize.retrieve(
            code="code",
            _state="_state",
        )
        assert authorize is None

    @pytest.mark.skip(reason="Prism doesn't properly handle redirects")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncQuark) -> None:
        response = await async_client.authorize.with_raw_response.retrieve(
            code="code",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        authorize = await response.parse()
        assert authorize is None

    @pytest.mark.skip(reason="Prism doesn't properly handle redirects")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncQuark) -> None:
        async with async_client.authorize.with_streaming_response.retrieve(
            code="code",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            authorize = await response.parse()
            assert authorize is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism doesn't properly handle redirects")
    @parametrize
    async def test_method_logout(self, async_client: AsyncQuark) -> None:
        authorize = await async_client.authorize.logout()
        assert authorize is None

    @pytest.mark.skip(reason="Prism doesn't properly handle redirects")
    @parametrize
    async def test_raw_response_logout(self, async_client: AsyncQuark) -> None:
        response = await async_client.authorize.with_raw_response.logout()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        authorize = await response.parse()
        assert authorize is None

    @pytest.mark.skip(reason="Prism doesn't properly handle redirects")
    @parametrize
    async def test_streaming_response_logout(self, async_client: AsyncQuark) -> None:
        async with async_client.authorize.with_streaming_response.logout() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            authorize = await response.parse()
            assert authorize is None

        assert cast(Any, response.is_closed) is True
