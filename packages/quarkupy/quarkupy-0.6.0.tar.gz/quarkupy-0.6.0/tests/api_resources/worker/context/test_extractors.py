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


class TestExtractors:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_method_list(self, client: Quark, respx_mock: MockRouter) -> None:
        respx_mock.get("/worker/context/extractors").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        extractor = client.worker.context.extractors.list()
        assert extractor.is_closed
        assert extractor.json() == {"foo": "bar"}
        assert cast(Any, extractor.is_closed) is True
        assert isinstance(extractor, BinaryAPIResponse)

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_method_list_with_all_params(self, client: Quark, respx_mock: MockRouter) -> None:
        respx_mock.get("/worker/context/extractors").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        extractor = client.worker.context.extractors.list(
            limit=0,
            offset=0,
            source_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert extractor.is_closed
        assert extractor.json() == {"foo": "bar"}
        assert cast(Any, extractor.is_closed) is True
        assert isinstance(extractor, BinaryAPIResponse)

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_raw_response_list(self, client: Quark, respx_mock: MockRouter) -> None:
        respx_mock.get("/worker/context/extractors").mock(return_value=httpx.Response(200, json={"foo": "bar"}))

        extractor = client.worker.context.extractors.with_raw_response.list()

        assert extractor.is_closed is True
        assert extractor.http_request.headers.get("X-Stainless-Lang") == "python"
        assert extractor.json() == {"foo": "bar"}
        assert isinstance(extractor, BinaryAPIResponse)

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_streaming_response_list(self, client: Quark, respx_mock: MockRouter) -> None:
        respx_mock.get("/worker/context/extractors").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        with client.worker.context.extractors.with_streaming_response.list() as extractor:
            assert not extractor.is_closed
            assert extractor.http_request.headers.get("X-Stainless-Lang") == "python"

            assert extractor.json() == {"foo": "bar"}
            assert cast(Any, extractor.is_closed) is True
            assert isinstance(extractor, StreamedBinaryAPIResponse)

        assert cast(Any, extractor.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_method_retrieve_text(self, client: Quark, respx_mock: MockRouter) -> None:
        respx_mock.get("/worker/context/extractors/182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e/text").mock(
            return_value=httpx.Response(200, json={"foo": "bar"})
        )
        extractor = client.worker.context.extractors.retrieve_text(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert extractor.is_closed
        assert extractor.json() == {"foo": "bar"}
        assert cast(Any, extractor.is_closed) is True
        assert isinstance(extractor, BinaryAPIResponse)

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_raw_response_retrieve_text(self, client: Quark, respx_mock: MockRouter) -> None:
        respx_mock.get("/worker/context/extractors/182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e/text").mock(
            return_value=httpx.Response(200, json={"foo": "bar"})
        )

        extractor = client.worker.context.extractors.with_raw_response.retrieve_text(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert extractor.is_closed is True
        assert extractor.http_request.headers.get("X-Stainless-Lang") == "python"
        assert extractor.json() == {"foo": "bar"}
        assert isinstance(extractor, BinaryAPIResponse)

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_streaming_response_retrieve_text(self, client: Quark, respx_mock: MockRouter) -> None:
        respx_mock.get("/worker/context/extractors/182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e/text").mock(
            return_value=httpx.Response(200, json={"foo": "bar"})
        )
        with client.worker.context.extractors.with_streaming_response.retrieve_text(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as extractor:
            assert not extractor.is_closed
            assert extractor.http_request.headers.get("X-Stainless-Lang") == "python"

            assert extractor.json() == {"foo": "bar"}
            assert cast(Any, extractor.is_closed) is True
            assert isinstance(extractor, StreamedBinaryAPIResponse)

        assert cast(Any, extractor.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_path_params_retrieve_text(self, client: Quark) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `extractor_id` but received ''"):
            client.worker.context.extractors.with_raw_response.retrieve_text(
                "",
            )


class TestAsyncExtractors:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_method_list(self, async_client: AsyncQuark, respx_mock: MockRouter) -> None:
        respx_mock.get("/worker/context/extractors").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        extractor = await async_client.worker.context.extractors.list()
        assert extractor.is_closed
        assert await extractor.json() == {"foo": "bar"}
        assert cast(Any, extractor.is_closed) is True
        assert isinstance(extractor, AsyncBinaryAPIResponse)

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_method_list_with_all_params(self, async_client: AsyncQuark, respx_mock: MockRouter) -> None:
        respx_mock.get("/worker/context/extractors").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        extractor = await async_client.worker.context.extractors.list(
            limit=0,
            offset=0,
            source_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert extractor.is_closed
        assert await extractor.json() == {"foo": "bar"}
        assert cast(Any, extractor.is_closed) is True
        assert isinstance(extractor, AsyncBinaryAPIResponse)

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_raw_response_list(self, async_client: AsyncQuark, respx_mock: MockRouter) -> None:
        respx_mock.get("/worker/context/extractors").mock(return_value=httpx.Response(200, json={"foo": "bar"}))

        extractor = await async_client.worker.context.extractors.with_raw_response.list()

        assert extractor.is_closed is True
        assert extractor.http_request.headers.get("X-Stainless-Lang") == "python"
        assert await extractor.json() == {"foo": "bar"}
        assert isinstance(extractor, AsyncBinaryAPIResponse)

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_streaming_response_list(self, async_client: AsyncQuark, respx_mock: MockRouter) -> None:
        respx_mock.get("/worker/context/extractors").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        async with async_client.worker.context.extractors.with_streaming_response.list() as extractor:
            assert not extractor.is_closed
            assert extractor.http_request.headers.get("X-Stainless-Lang") == "python"

            assert await extractor.json() == {"foo": "bar"}
            assert cast(Any, extractor.is_closed) is True
            assert isinstance(extractor, AsyncStreamedBinaryAPIResponse)

        assert cast(Any, extractor.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_method_retrieve_text(self, async_client: AsyncQuark, respx_mock: MockRouter) -> None:
        respx_mock.get("/worker/context/extractors/182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e/text").mock(
            return_value=httpx.Response(200, json={"foo": "bar"})
        )
        extractor = await async_client.worker.context.extractors.retrieve_text(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert extractor.is_closed
        assert await extractor.json() == {"foo": "bar"}
        assert cast(Any, extractor.is_closed) is True
        assert isinstance(extractor, AsyncBinaryAPIResponse)

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_raw_response_retrieve_text(self, async_client: AsyncQuark, respx_mock: MockRouter) -> None:
        respx_mock.get("/worker/context/extractors/182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e/text").mock(
            return_value=httpx.Response(200, json={"foo": "bar"})
        )

        extractor = await async_client.worker.context.extractors.with_raw_response.retrieve_text(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert extractor.is_closed is True
        assert extractor.http_request.headers.get("X-Stainless-Lang") == "python"
        assert await extractor.json() == {"foo": "bar"}
        assert isinstance(extractor, AsyncBinaryAPIResponse)

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_streaming_response_retrieve_text(self, async_client: AsyncQuark, respx_mock: MockRouter) -> None:
        respx_mock.get("/worker/context/extractors/182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e/text").mock(
            return_value=httpx.Response(200, json={"foo": "bar"})
        )
        async with async_client.worker.context.extractors.with_streaming_response.retrieve_text(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as extractor:
            assert not extractor.is_closed
            assert extractor.http_request.headers.get("X-Stainless-Lang") == "python"

            assert await extractor.json() == {"foo": "bar"}
            assert cast(Any, extractor.is_closed) is True
            assert isinstance(extractor, AsyncStreamedBinaryAPIResponse)

        assert cast(Any, extractor.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_path_params_retrieve_text(self, async_client: AsyncQuark) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `extractor_id` but received ''"):
            await async_client.worker.context.extractors.with_raw_response.retrieve_text(
                "",
            )
