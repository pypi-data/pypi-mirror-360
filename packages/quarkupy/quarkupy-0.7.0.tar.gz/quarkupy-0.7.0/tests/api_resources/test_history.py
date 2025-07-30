# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from quarkupy import Quark, AsyncQuark
from tests.utils import assert_matches_type
from quarkupy.types import (
    HistoryListResponse,
    HistoryListFlowsResponse,
    HistoryListQuarksResponse,
)
from quarkupy._utils import parse_datetime
from quarkupy.types.context import SuccessResponseMessage

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestHistory:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_list(self, client: Quark) -> None:
        history = client.history.list()
        assert_matches_type(HistoryListResponse, history, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_list(self, client: Quark) -> None:
        response = client.history.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        history = response.parse()
        assert_matches_type(HistoryListResponse, history, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_list(self, client: Quark) -> None:
        with client.history.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            history = response.parse()
            assert_matches_type(HistoryListResponse, history, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_clear_all(self, client: Quark) -> None:
        history = client.history.clear_all()
        assert_matches_type(SuccessResponseMessage, history, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_clear_all(self, client: Quark) -> None:
        response = client.history.with_raw_response.clear_all()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        history = response.parse()
        assert_matches_type(SuccessResponseMessage, history, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_clear_all(self, client: Quark) -> None:
        with client.history.with_streaming_response.clear_all() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            history = response.parse()
            assert_matches_type(SuccessResponseMessage, history, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_list_flows(self, client: Quark) -> None:
        history = client.history.list_flows()
        assert_matches_type(HistoryListFlowsResponse, history, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_list_flows_with_all_params(self, client: Quark) -> None:
        history = client.history.list_flows(
            max_timestamp=parse_datetime("2019-12-27T18:11:19.117Z"),
            min_timestamp=parse_datetime("2019-12-27T18:11:19.117Z"),
            registry_identifier="registry_identifier",
        )
        assert_matches_type(HistoryListFlowsResponse, history, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_list_flows(self, client: Quark) -> None:
        response = client.history.with_raw_response.list_flows()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        history = response.parse()
        assert_matches_type(HistoryListFlowsResponse, history, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_list_flows(self, client: Quark) -> None:
        with client.history.with_streaming_response.list_flows() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            history = response.parse()
            assert_matches_type(HistoryListFlowsResponse, history, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_list_quarks(self, client: Quark) -> None:
        history = client.history.list_quarks()
        assert_matches_type(HistoryListQuarksResponse, history, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_list_quarks_with_all_params(self, client: Quark) -> None:
        history = client.history.list_quarks(
            lattice_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            max_timestamp=parse_datetime("2019-12-27T18:11:19.117Z"),
            min_timestamp=parse_datetime("2019-12-27T18:11:19.117Z"),
            registry_identifier="registry_identifier",
        )
        assert_matches_type(HistoryListQuarksResponse, history, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_list_quarks(self, client: Quark) -> None:
        response = client.history.with_raw_response.list_quarks()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        history = response.parse()
        assert_matches_type(HistoryListQuarksResponse, history, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_list_quarks(self, client: Quark) -> None:
        with client.history.with_streaming_response.list_quarks() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            history = response.parse()
            assert_matches_type(HistoryListQuarksResponse, history, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncHistory:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_list(self, async_client: AsyncQuark) -> None:
        history = await async_client.history.list()
        assert_matches_type(HistoryListResponse, history, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncQuark) -> None:
        response = await async_client.history.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        history = await response.parse()
        assert_matches_type(HistoryListResponse, history, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncQuark) -> None:
        async with async_client.history.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            history = await response.parse()
            assert_matches_type(HistoryListResponse, history, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_clear_all(self, async_client: AsyncQuark) -> None:
        history = await async_client.history.clear_all()
        assert_matches_type(SuccessResponseMessage, history, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_clear_all(self, async_client: AsyncQuark) -> None:
        response = await async_client.history.with_raw_response.clear_all()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        history = await response.parse()
        assert_matches_type(SuccessResponseMessage, history, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_clear_all(self, async_client: AsyncQuark) -> None:
        async with async_client.history.with_streaming_response.clear_all() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            history = await response.parse()
            assert_matches_type(SuccessResponseMessage, history, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_list_flows(self, async_client: AsyncQuark) -> None:
        history = await async_client.history.list_flows()
        assert_matches_type(HistoryListFlowsResponse, history, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_list_flows_with_all_params(self, async_client: AsyncQuark) -> None:
        history = await async_client.history.list_flows(
            max_timestamp=parse_datetime("2019-12-27T18:11:19.117Z"),
            min_timestamp=parse_datetime("2019-12-27T18:11:19.117Z"),
            registry_identifier="registry_identifier",
        )
        assert_matches_type(HistoryListFlowsResponse, history, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_list_flows(self, async_client: AsyncQuark) -> None:
        response = await async_client.history.with_raw_response.list_flows()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        history = await response.parse()
        assert_matches_type(HistoryListFlowsResponse, history, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_list_flows(self, async_client: AsyncQuark) -> None:
        async with async_client.history.with_streaming_response.list_flows() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            history = await response.parse()
            assert_matches_type(HistoryListFlowsResponse, history, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_list_quarks(self, async_client: AsyncQuark) -> None:
        history = await async_client.history.list_quarks()
        assert_matches_type(HistoryListQuarksResponse, history, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_list_quarks_with_all_params(self, async_client: AsyncQuark) -> None:
        history = await async_client.history.list_quarks(
            lattice_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            max_timestamp=parse_datetime("2019-12-27T18:11:19.117Z"),
            min_timestamp=parse_datetime("2019-12-27T18:11:19.117Z"),
            registry_identifier="registry_identifier",
        )
        assert_matches_type(HistoryListQuarksResponse, history, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_list_quarks(self, async_client: AsyncQuark) -> None:
        response = await async_client.history.with_raw_response.list_quarks()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        history = await response.parse()
        assert_matches_type(HistoryListQuarksResponse, history, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_list_quarks(self, async_client: AsyncQuark) -> None:
        async with async_client.history.with_streaming_response.list_quarks() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            history = await response.parse()
            assert_matches_type(HistoryListQuarksResponse, history, path=["response"])

        assert cast(Any, response.is_closed) is True
