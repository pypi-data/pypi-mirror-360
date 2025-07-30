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


class TestClassifiers:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_method_list(self, client: Quark, respx_mock: MockRouter) -> None:
        respx_mock.get("/worker/context/classifiers").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        classifier = client.worker.context.classifiers.list()
        assert classifier.is_closed
        assert classifier.json() == {"foo": "bar"}
        assert cast(Any, classifier.is_closed) is True
        assert isinstance(classifier, BinaryAPIResponse)

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_method_list_with_all_params(self, client: Quark, respx_mock: MockRouter) -> None:
        respx_mock.get("/worker/context/classifiers").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        classifier = client.worker.context.classifiers.list(
            limit=0,
            offset=0,
            source_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert classifier.is_closed
        assert classifier.json() == {"foo": "bar"}
        assert cast(Any, classifier.is_closed) is True
        assert isinstance(classifier, BinaryAPIResponse)

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_raw_response_list(self, client: Quark, respx_mock: MockRouter) -> None:
        respx_mock.get("/worker/context/classifiers").mock(return_value=httpx.Response(200, json={"foo": "bar"}))

        classifier = client.worker.context.classifiers.with_raw_response.list()

        assert classifier.is_closed is True
        assert classifier.http_request.headers.get("X-Stainless-Lang") == "python"
        assert classifier.json() == {"foo": "bar"}
        assert isinstance(classifier, BinaryAPIResponse)

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_streaming_response_list(self, client: Quark, respx_mock: MockRouter) -> None:
        respx_mock.get("/worker/context/classifiers").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        with client.worker.context.classifiers.with_streaming_response.list() as classifier:
            assert not classifier.is_closed
            assert classifier.http_request.headers.get("X-Stainless-Lang") == "python"

            assert classifier.json() == {"foo": "bar"}
            assert cast(Any, classifier.is_closed) is True
            assert isinstance(classifier, StreamedBinaryAPIResponse)

        assert cast(Any, classifier.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_method_retrieve_text(self, client: Quark, respx_mock: MockRouter) -> None:
        respx_mock.get("/worker/context/classifiers/182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e/text").mock(
            return_value=httpx.Response(200, json={"foo": "bar"})
        )
        classifier = client.worker.context.classifiers.retrieve_text(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert classifier.is_closed
        assert classifier.json() == {"foo": "bar"}
        assert cast(Any, classifier.is_closed) is True
        assert isinstance(classifier, BinaryAPIResponse)

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_raw_response_retrieve_text(self, client: Quark, respx_mock: MockRouter) -> None:
        respx_mock.get("/worker/context/classifiers/182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e/text").mock(
            return_value=httpx.Response(200, json={"foo": "bar"})
        )

        classifier = client.worker.context.classifiers.with_raw_response.retrieve_text(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert classifier.is_closed is True
        assert classifier.http_request.headers.get("X-Stainless-Lang") == "python"
        assert classifier.json() == {"foo": "bar"}
        assert isinstance(classifier, BinaryAPIResponse)

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_streaming_response_retrieve_text(self, client: Quark, respx_mock: MockRouter) -> None:
        respx_mock.get("/worker/context/classifiers/182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e/text").mock(
            return_value=httpx.Response(200, json={"foo": "bar"})
        )
        with client.worker.context.classifiers.with_streaming_response.retrieve_text(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as classifier:
            assert not classifier.is_closed
            assert classifier.http_request.headers.get("X-Stainless-Lang") == "python"

            assert classifier.json() == {"foo": "bar"}
            assert cast(Any, classifier.is_closed) is True
            assert isinstance(classifier, StreamedBinaryAPIResponse)

        assert cast(Any, classifier.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_path_params_retrieve_text(self, client: Quark) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `classifier_id` but received ''"):
            client.worker.context.classifiers.with_raw_response.retrieve_text(
                "",
            )


class TestAsyncClassifiers:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_method_list(self, async_client: AsyncQuark, respx_mock: MockRouter) -> None:
        respx_mock.get("/worker/context/classifiers").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        classifier = await async_client.worker.context.classifiers.list()
        assert classifier.is_closed
        assert await classifier.json() == {"foo": "bar"}
        assert cast(Any, classifier.is_closed) is True
        assert isinstance(classifier, AsyncBinaryAPIResponse)

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_method_list_with_all_params(self, async_client: AsyncQuark, respx_mock: MockRouter) -> None:
        respx_mock.get("/worker/context/classifiers").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        classifier = await async_client.worker.context.classifiers.list(
            limit=0,
            offset=0,
            source_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert classifier.is_closed
        assert await classifier.json() == {"foo": "bar"}
        assert cast(Any, classifier.is_closed) is True
        assert isinstance(classifier, AsyncBinaryAPIResponse)

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_raw_response_list(self, async_client: AsyncQuark, respx_mock: MockRouter) -> None:
        respx_mock.get("/worker/context/classifiers").mock(return_value=httpx.Response(200, json={"foo": "bar"}))

        classifier = await async_client.worker.context.classifiers.with_raw_response.list()

        assert classifier.is_closed is True
        assert classifier.http_request.headers.get("X-Stainless-Lang") == "python"
        assert await classifier.json() == {"foo": "bar"}
        assert isinstance(classifier, AsyncBinaryAPIResponse)

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_streaming_response_list(self, async_client: AsyncQuark, respx_mock: MockRouter) -> None:
        respx_mock.get("/worker/context/classifiers").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        async with async_client.worker.context.classifiers.with_streaming_response.list() as classifier:
            assert not classifier.is_closed
            assert classifier.http_request.headers.get("X-Stainless-Lang") == "python"

            assert await classifier.json() == {"foo": "bar"}
            assert cast(Any, classifier.is_closed) is True
            assert isinstance(classifier, AsyncStreamedBinaryAPIResponse)

        assert cast(Any, classifier.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_method_retrieve_text(self, async_client: AsyncQuark, respx_mock: MockRouter) -> None:
        respx_mock.get("/worker/context/classifiers/182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e/text").mock(
            return_value=httpx.Response(200, json={"foo": "bar"})
        )
        classifier = await async_client.worker.context.classifiers.retrieve_text(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert classifier.is_closed
        assert await classifier.json() == {"foo": "bar"}
        assert cast(Any, classifier.is_closed) is True
        assert isinstance(classifier, AsyncBinaryAPIResponse)

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_raw_response_retrieve_text(self, async_client: AsyncQuark, respx_mock: MockRouter) -> None:
        respx_mock.get("/worker/context/classifiers/182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e/text").mock(
            return_value=httpx.Response(200, json={"foo": "bar"})
        )

        classifier = await async_client.worker.context.classifiers.with_raw_response.retrieve_text(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert classifier.is_closed is True
        assert classifier.http_request.headers.get("X-Stainless-Lang") == "python"
        assert await classifier.json() == {"foo": "bar"}
        assert isinstance(classifier, AsyncBinaryAPIResponse)

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_streaming_response_retrieve_text(self, async_client: AsyncQuark, respx_mock: MockRouter) -> None:
        respx_mock.get("/worker/context/classifiers/182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e/text").mock(
            return_value=httpx.Response(200, json={"foo": "bar"})
        )
        async with async_client.worker.context.classifiers.with_streaming_response.retrieve_text(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as classifier:
            assert not classifier.is_closed
            assert classifier.http_request.headers.get("X-Stainless-Lang") == "python"

            assert await classifier.json() == {"foo": "bar"}
            assert cast(Any, classifier.is_closed) is True
            assert isinstance(classifier, AsyncStreamedBinaryAPIResponse)

        assert cast(Any, classifier.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_path_params_retrieve_text(self, async_client: AsyncQuark) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `classifier_id` but received ''"):
            await async_client.worker.context.classifiers.with_raw_response.retrieve_text(
                "",
            )
