# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import httpx
import pytest
from respx import MockRouter

from quarkupy import Quark, AsyncQuark
from quarkupy._response import (
    BinaryAPIResponse,
    AsyncBinaryAPIResponse,
    StreamedBinaryAPIResponse,
    AsyncStreamedBinaryAPIResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestContext:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_method_retrieve_files(self, client: Quark, respx_mock: MockRouter) -> None:
        respx_mock.get("/worker/context/files").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        context = client.worker.context.retrieve_files()
        assert context.is_closed
        assert context.json() == {"foo": "bar"}
        assert cast(Any, context.is_closed) is True
        assert isinstance(context, BinaryAPIResponse)

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_method_retrieve_files_with_all_params(self, client: Quark, respx_mock: MockRouter) -> None:
        respx_mock.get("/worker/context/files").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        context = client.worker.context.retrieve_files(
            limit=0,
            offset=0,
            source_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert context.is_closed
        assert context.json() == {"foo": "bar"}
        assert cast(Any, context.is_closed) is True
        assert isinstance(context, BinaryAPIResponse)

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_raw_response_retrieve_files(self, client: Quark, respx_mock: MockRouter) -> None:
        respx_mock.get("/worker/context/files").mock(return_value=httpx.Response(200, json={"foo": "bar"}))

        context = client.worker.context.with_raw_response.retrieve_files()

        assert context.is_closed is True
        assert context.http_request.headers.get("X-Stainless-Lang") == "python"
        assert context.json() == {"foo": "bar"}
        assert isinstance(context, BinaryAPIResponse)

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_streaming_response_retrieve_files(self, client: Quark, respx_mock: MockRouter) -> None:
        respx_mock.get("/worker/context/files").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        with client.worker.context.with_streaming_response.retrieve_files() as context:
            assert not context.is_closed
            assert context.http_request.headers.get("X-Stainless-Lang") == "python"

            assert context.json() == {"foo": "bar"}
            assert cast(Any, context.is_closed) is True
            assert isinstance(context, StreamedBinaryAPIResponse)

        assert cast(Any, context.is_closed) is True


class TestAsyncContext:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_method_retrieve_files(self, async_client: AsyncQuark, respx_mock: MockRouter) -> None:
        respx_mock.get("/worker/context/files").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        context = await async_client.worker.context.retrieve_files()
        assert context.is_closed
        assert await context.json() == {"foo": "bar"}
        assert cast(Any, context.is_closed) is True
        assert isinstance(context, AsyncBinaryAPIResponse)

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_method_retrieve_files_with_all_params(
        self, async_client: AsyncQuark, respx_mock: MockRouter
    ) -> None:
        respx_mock.get("/worker/context/files").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        context = await async_client.worker.context.retrieve_files(
            limit=0,
            offset=0,
            source_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert context.is_closed
        assert await context.json() == {"foo": "bar"}
        assert cast(Any, context.is_closed) is True
        assert isinstance(context, AsyncBinaryAPIResponse)

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_raw_response_retrieve_files(self, async_client: AsyncQuark, respx_mock: MockRouter) -> None:
        respx_mock.get("/worker/context/files").mock(return_value=httpx.Response(200, json={"foo": "bar"}))

        context = await async_client.worker.context.with_raw_response.retrieve_files()

        assert context.is_closed is True
        assert context.http_request.headers.get("X-Stainless-Lang") == "python"
        assert await context.json() == {"foo": "bar"}
        assert isinstance(context, AsyncBinaryAPIResponse)

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_streaming_response_retrieve_files(self, async_client: AsyncQuark, respx_mock: MockRouter) -> None:
        respx_mock.get("/worker/context/files").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        async with async_client.worker.context.with_streaming_response.retrieve_files() as context:
            assert not context.is_closed
            assert context.http_request.headers.get("X-Stainless-Lang") == "python"

            assert await context.json() == {"foo": "bar"}
            assert cast(Any, context.is_closed) is True
            assert isinstance(context, AsyncStreamedBinaryAPIResponse)

        assert cast(Any, context.is_closed) is True
