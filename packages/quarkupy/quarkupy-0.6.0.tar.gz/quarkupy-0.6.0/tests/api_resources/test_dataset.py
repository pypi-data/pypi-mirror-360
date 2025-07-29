# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import httpx
import pytest
from respx import MockRouter

from quarkupy import Quark, AsyncQuark
from tests.utils import assert_matches_type
from quarkupy.types import (
    DataSetInfo,
    DatasetListResponse,
)
from quarkupy._response import (
    BinaryAPIResponse,
    AsyncBinaryAPIResponse,
    StreamedBinaryAPIResponse,
    AsyncStreamedBinaryAPIResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestDataset:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve(self, client: Quark) -> None:
        dataset = client.dataset.retrieve(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(DataSetInfo, dataset, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_retrieve(self, client: Quark) -> None:
        response = client.dataset.with_raw_response.retrieve(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        dataset = response.parse()
        assert_matches_type(DataSetInfo, dataset, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_retrieve(self, client: Quark) -> None:
        with client.dataset.with_streaming_response.retrieve(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            dataset = response.parse()
            assert_matches_type(DataSetInfo, dataset, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_retrieve(self, client: Quark) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.dataset.with_raw_response.retrieve(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_list(self, client: Quark) -> None:
        dataset = client.dataset.list()
        assert_matches_type(DatasetListResponse, dataset, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_list(self, client: Quark) -> None:
        response = client.dataset.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        dataset = response.parse()
        assert_matches_type(DatasetListResponse, dataset, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_list(self, client: Quark) -> None:
        with client.dataset.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            dataset = response.parse()
            assert_matches_type(DatasetListResponse, dataset, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_method_retrieve_arrow(self, client: Quark, respx_mock: MockRouter) -> None:
        respx_mock.get("/dataset/182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e/arrow").mock(
            return_value=httpx.Response(200, json={"foo": "bar"})
        )
        dataset = client.dataset.retrieve_arrow(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert dataset.is_closed
        assert dataset.json() == {"foo": "bar"}
        assert cast(Any, dataset.is_closed) is True
        assert isinstance(dataset, BinaryAPIResponse)

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_method_retrieve_arrow_with_all_params(self, client: Quark, respx_mock: MockRouter) -> None:
        respx_mock.get("/dataset/182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e/arrow").mock(
            return_value=httpx.Response(200, json={"foo": "bar"})
        )
        dataset = client.dataset.retrieve_arrow(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            _limit=0,
            _offset=0,
        )
        assert dataset.is_closed
        assert dataset.json() == {"foo": "bar"}
        assert cast(Any, dataset.is_closed) is True
        assert isinstance(dataset, BinaryAPIResponse)

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_raw_response_retrieve_arrow(self, client: Quark, respx_mock: MockRouter) -> None:
        respx_mock.get("/dataset/182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e/arrow").mock(
            return_value=httpx.Response(200, json={"foo": "bar"})
        )

        dataset = client.dataset.with_raw_response.retrieve_arrow(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert dataset.is_closed is True
        assert dataset.http_request.headers.get("X-Stainless-Lang") == "python"
        assert dataset.json() == {"foo": "bar"}
        assert isinstance(dataset, BinaryAPIResponse)

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_streaming_response_retrieve_arrow(self, client: Quark, respx_mock: MockRouter) -> None:
        respx_mock.get("/dataset/182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e/arrow").mock(
            return_value=httpx.Response(200, json={"foo": "bar"})
        )
        with client.dataset.with_streaming_response.retrieve_arrow(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as dataset:
            assert not dataset.is_closed
            assert dataset.http_request.headers.get("X-Stainless-Lang") == "python"

            assert dataset.json() == {"foo": "bar"}
            assert cast(Any, dataset.is_closed) is True
            assert isinstance(dataset, StreamedBinaryAPIResponse)

        assert cast(Any, dataset.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_path_params_retrieve_arrow(self, client: Quark) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.dataset.with_raw_response.retrieve_arrow(
                id="",
            )

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_method_retrieve_chunks(self, client: Quark, respx_mock: MockRouter) -> None:
        respx_mock.get(
            "/dataset/182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e/182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e/chunks"
        ).mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        dataset = client.dataset.retrieve_chunks(
            file_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert dataset.is_closed
        assert dataset.json() == {"foo": "bar"}
        assert cast(Any, dataset.is_closed) is True
        assert isinstance(dataset, BinaryAPIResponse)

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_method_retrieve_chunks_with_all_params(self, client: Quark, respx_mock: MockRouter) -> None:
        respx_mock.get(
            "/dataset/182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e/182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e/chunks"
        ).mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        dataset = client.dataset.retrieve_chunks(
            file_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            _limit=0,
            _offset=0,
        )
        assert dataset.is_closed
        assert dataset.json() == {"foo": "bar"}
        assert cast(Any, dataset.is_closed) is True
        assert isinstance(dataset, BinaryAPIResponse)

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_raw_response_retrieve_chunks(self, client: Quark, respx_mock: MockRouter) -> None:
        respx_mock.get(
            "/dataset/182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e/182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e/chunks"
        ).mock(return_value=httpx.Response(200, json={"foo": "bar"}))

        dataset = client.dataset.with_raw_response.retrieve_chunks(
            file_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert dataset.is_closed is True
        assert dataset.http_request.headers.get("X-Stainless-Lang") == "python"
        assert dataset.json() == {"foo": "bar"}
        assert isinstance(dataset, BinaryAPIResponse)

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_streaming_response_retrieve_chunks(self, client: Quark, respx_mock: MockRouter) -> None:
        respx_mock.get(
            "/dataset/182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e/182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e/chunks"
        ).mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        with client.dataset.with_streaming_response.retrieve_chunks(
            file_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as dataset:
            assert not dataset.is_closed
            assert dataset.http_request.headers.get("X-Stainless-Lang") == "python"

            assert dataset.json() == {"foo": "bar"}
            assert cast(Any, dataset.is_closed) is True
            assert isinstance(dataset, StreamedBinaryAPIResponse)

        assert cast(Any, dataset.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_path_params_retrieve_chunks(self, client: Quark) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.dataset.with_raw_response.retrieve_chunks(
                file_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `file_id` but received ''"):
            client.dataset.with_raw_response.retrieve_chunks(
                file_id="",
                id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve_csv(self, client: Quark) -> None:
        dataset = client.dataset.retrieve_csv(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(str, dataset, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve_csv_with_all_params(self, client: Quark) -> None:
        dataset = client.dataset.retrieve_csv(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            limit=0,
            offset=0,
        )
        assert_matches_type(str, dataset, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_retrieve_csv(self, client: Quark) -> None:
        response = client.dataset.with_raw_response.retrieve_csv(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        dataset = response.parse()
        assert_matches_type(str, dataset, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_retrieve_csv(self, client: Quark) -> None:
        with client.dataset.with_streaming_response.retrieve_csv(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            dataset = response.parse()
            assert_matches_type(str, dataset, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_retrieve_csv(self, client: Quark) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.dataset.with_raw_response.retrieve_csv(
                id="",
            )

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_method_retrieve_files(self, client: Quark, respx_mock: MockRouter) -> None:
        respx_mock.get("/dataset/182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e/files").mock(
            return_value=httpx.Response(200, json={"foo": "bar"})
        )
        dataset = client.dataset.retrieve_files(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert dataset.is_closed
        assert dataset.json() == {"foo": "bar"}
        assert cast(Any, dataset.is_closed) is True
        assert isinstance(dataset, BinaryAPIResponse)

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_method_retrieve_files_with_all_params(self, client: Quark, respx_mock: MockRouter) -> None:
        respx_mock.get("/dataset/182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e/files").mock(
            return_value=httpx.Response(200, json={"foo": "bar"})
        )
        dataset = client.dataset.retrieve_files(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            _limit=0,
            _offset=0,
        )
        assert dataset.is_closed
        assert dataset.json() == {"foo": "bar"}
        assert cast(Any, dataset.is_closed) is True
        assert isinstance(dataset, BinaryAPIResponse)

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_raw_response_retrieve_files(self, client: Quark, respx_mock: MockRouter) -> None:
        respx_mock.get("/dataset/182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e/files").mock(
            return_value=httpx.Response(200, json={"foo": "bar"})
        )

        dataset = client.dataset.with_raw_response.retrieve_files(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert dataset.is_closed is True
        assert dataset.http_request.headers.get("X-Stainless-Lang") == "python"
        assert dataset.json() == {"foo": "bar"}
        assert isinstance(dataset, BinaryAPIResponse)

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_streaming_response_retrieve_files(self, client: Quark, respx_mock: MockRouter) -> None:
        respx_mock.get("/dataset/182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e/files").mock(
            return_value=httpx.Response(200, json={"foo": "bar"})
        )
        with client.dataset.with_streaming_response.retrieve_files(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as dataset:
            assert not dataset.is_closed
            assert dataset.http_request.headers.get("X-Stainless-Lang") == "python"

            assert dataset.json() == {"foo": "bar"}
            assert cast(Any, dataset.is_closed) is True
            assert isinstance(dataset, StreamedBinaryAPIResponse)

        assert cast(Any, dataset.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_path_params_retrieve_files(self, client: Quark) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.dataset.with_raw_response.retrieve_files(
                id="",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve_json(self, client: Quark) -> None:
        dataset = client.dataset.retrieve_json(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(str, dataset, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve_json_with_all_params(self, client: Quark) -> None:
        dataset = client.dataset.retrieve_json(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            max_cell_size=0,
        )
        assert_matches_type(str, dataset, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_retrieve_json(self, client: Quark) -> None:
        response = client.dataset.with_raw_response.retrieve_json(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        dataset = response.parse()
        assert_matches_type(str, dataset, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_retrieve_json(self, client: Quark) -> None:
        with client.dataset.with_streaming_response.retrieve_json(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            dataset = response.parse()
            assert_matches_type(str, dataset, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_retrieve_json(self, client: Quark) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.dataset.with_raw_response.retrieve_json(
                id="",
            )


class TestAsyncDataset:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncQuark) -> None:
        dataset = await async_client.dataset.retrieve(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(DataSetInfo, dataset, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncQuark) -> None:
        response = await async_client.dataset.with_raw_response.retrieve(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        dataset = await response.parse()
        assert_matches_type(DataSetInfo, dataset, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncQuark) -> None:
        async with async_client.dataset.with_streaming_response.retrieve(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            dataset = await response.parse()
            assert_matches_type(DataSetInfo, dataset, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncQuark) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.dataset.with_raw_response.retrieve(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_list(self, async_client: AsyncQuark) -> None:
        dataset = await async_client.dataset.list()
        assert_matches_type(DatasetListResponse, dataset, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncQuark) -> None:
        response = await async_client.dataset.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        dataset = await response.parse()
        assert_matches_type(DatasetListResponse, dataset, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncQuark) -> None:
        async with async_client.dataset.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            dataset = await response.parse()
            assert_matches_type(DatasetListResponse, dataset, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_method_retrieve_arrow(self, async_client: AsyncQuark, respx_mock: MockRouter) -> None:
        respx_mock.get("/dataset/182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e/arrow").mock(
            return_value=httpx.Response(200, json={"foo": "bar"})
        )
        dataset = await async_client.dataset.retrieve_arrow(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert dataset.is_closed
        assert await dataset.json() == {"foo": "bar"}
        assert cast(Any, dataset.is_closed) is True
        assert isinstance(dataset, AsyncBinaryAPIResponse)

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_method_retrieve_arrow_with_all_params(
        self, async_client: AsyncQuark, respx_mock: MockRouter
    ) -> None:
        respx_mock.get("/dataset/182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e/arrow").mock(
            return_value=httpx.Response(200, json={"foo": "bar"})
        )
        dataset = await async_client.dataset.retrieve_arrow(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            _limit=0,
            _offset=0,
        )
        assert dataset.is_closed
        assert await dataset.json() == {"foo": "bar"}
        assert cast(Any, dataset.is_closed) is True
        assert isinstance(dataset, AsyncBinaryAPIResponse)

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_raw_response_retrieve_arrow(self, async_client: AsyncQuark, respx_mock: MockRouter) -> None:
        respx_mock.get("/dataset/182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e/arrow").mock(
            return_value=httpx.Response(200, json={"foo": "bar"})
        )

        dataset = await async_client.dataset.with_raw_response.retrieve_arrow(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert dataset.is_closed is True
        assert dataset.http_request.headers.get("X-Stainless-Lang") == "python"
        assert await dataset.json() == {"foo": "bar"}
        assert isinstance(dataset, AsyncBinaryAPIResponse)

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_streaming_response_retrieve_arrow(self, async_client: AsyncQuark, respx_mock: MockRouter) -> None:
        respx_mock.get("/dataset/182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e/arrow").mock(
            return_value=httpx.Response(200, json={"foo": "bar"})
        )
        async with async_client.dataset.with_streaming_response.retrieve_arrow(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as dataset:
            assert not dataset.is_closed
            assert dataset.http_request.headers.get("X-Stainless-Lang") == "python"

            assert await dataset.json() == {"foo": "bar"}
            assert cast(Any, dataset.is_closed) is True
            assert isinstance(dataset, AsyncStreamedBinaryAPIResponse)

        assert cast(Any, dataset.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_path_params_retrieve_arrow(self, async_client: AsyncQuark) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.dataset.with_raw_response.retrieve_arrow(
                id="",
            )

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_method_retrieve_chunks(self, async_client: AsyncQuark, respx_mock: MockRouter) -> None:
        respx_mock.get(
            "/dataset/182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e/182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e/chunks"
        ).mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        dataset = await async_client.dataset.retrieve_chunks(
            file_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert dataset.is_closed
        assert await dataset.json() == {"foo": "bar"}
        assert cast(Any, dataset.is_closed) is True
        assert isinstance(dataset, AsyncBinaryAPIResponse)

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_method_retrieve_chunks_with_all_params(
        self, async_client: AsyncQuark, respx_mock: MockRouter
    ) -> None:
        respx_mock.get(
            "/dataset/182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e/182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e/chunks"
        ).mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        dataset = await async_client.dataset.retrieve_chunks(
            file_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            _limit=0,
            _offset=0,
        )
        assert dataset.is_closed
        assert await dataset.json() == {"foo": "bar"}
        assert cast(Any, dataset.is_closed) is True
        assert isinstance(dataset, AsyncBinaryAPIResponse)

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_raw_response_retrieve_chunks(self, async_client: AsyncQuark, respx_mock: MockRouter) -> None:
        respx_mock.get(
            "/dataset/182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e/182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e/chunks"
        ).mock(return_value=httpx.Response(200, json={"foo": "bar"}))

        dataset = await async_client.dataset.with_raw_response.retrieve_chunks(
            file_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert dataset.is_closed is True
        assert dataset.http_request.headers.get("X-Stainless-Lang") == "python"
        assert await dataset.json() == {"foo": "bar"}
        assert isinstance(dataset, AsyncBinaryAPIResponse)

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_streaming_response_retrieve_chunks(self, async_client: AsyncQuark, respx_mock: MockRouter) -> None:
        respx_mock.get(
            "/dataset/182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e/182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e/chunks"
        ).mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        async with async_client.dataset.with_streaming_response.retrieve_chunks(
            file_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as dataset:
            assert not dataset.is_closed
            assert dataset.http_request.headers.get("X-Stainless-Lang") == "python"

            assert await dataset.json() == {"foo": "bar"}
            assert cast(Any, dataset.is_closed) is True
            assert isinstance(dataset, AsyncStreamedBinaryAPIResponse)

        assert cast(Any, dataset.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_path_params_retrieve_chunks(self, async_client: AsyncQuark) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.dataset.with_raw_response.retrieve_chunks(
                file_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `file_id` but received ''"):
            await async_client.dataset.with_raw_response.retrieve_chunks(
                file_id="",
                id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve_csv(self, async_client: AsyncQuark) -> None:
        dataset = await async_client.dataset.retrieve_csv(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(str, dataset, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve_csv_with_all_params(self, async_client: AsyncQuark) -> None:
        dataset = await async_client.dataset.retrieve_csv(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            limit=0,
            offset=0,
        )
        assert_matches_type(str, dataset, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_retrieve_csv(self, async_client: AsyncQuark) -> None:
        response = await async_client.dataset.with_raw_response.retrieve_csv(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        dataset = await response.parse()
        assert_matches_type(str, dataset, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_retrieve_csv(self, async_client: AsyncQuark) -> None:
        async with async_client.dataset.with_streaming_response.retrieve_csv(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            dataset = await response.parse()
            assert_matches_type(str, dataset, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_retrieve_csv(self, async_client: AsyncQuark) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.dataset.with_raw_response.retrieve_csv(
                id="",
            )

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_method_retrieve_files(self, async_client: AsyncQuark, respx_mock: MockRouter) -> None:
        respx_mock.get("/dataset/182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e/files").mock(
            return_value=httpx.Response(200, json={"foo": "bar"})
        )
        dataset = await async_client.dataset.retrieve_files(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert dataset.is_closed
        assert await dataset.json() == {"foo": "bar"}
        assert cast(Any, dataset.is_closed) is True
        assert isinstance(dataset, AsyncBinaryAPIResponse)

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_method_retrieve_files_with_all_params(
        self, async_client: AsyncQuark, respx_mock: MockRouter
    ) -> None:
        respx_mock.get("/dataset/182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e/files").mock(
            return_value=httpx.Response(200, json={"foo": "bar"})
        )
        dataset = await async_client.dataset.retrieve_files(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            _limit=0,
            _offset=0,
        )
        assert dataset.is_closed
        assert await dataset.json() == {"foo": "bar"}
        assert cast(Any, dataset.is_closed) is True
        assert isinstance(dataset, AsyncBinaryAPIResponse)

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_raw_response_retrieve_files(self, async_client: AsyncQuark, respx_mock: MockRouter) -> None:
        respx_mock.get("/dataset/182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e/files").mock(
            return_value=httpx.Response(200, json={"foo": "bar"})
        )

        dataset = await async_client.dataset.with_raw_response.retrieve_files(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert dataset.is_closed is True
        assert dataset.http_request.headers.get("X-Stainless-Lang") == "python"
        assert await dataset.json() == {"foo": "bar"}
        assert isinstance(dataset, AsyncBinaryAPIResponse)

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_streaming_response_retrieve_files(self, async_client: AsyncQuark, respx_mock: MockRouter) -> None:
        respx_mock.get("/dataset/182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e/files").mock(
            return_value=httpx.Response(200, json={"foo": "bar"})
        )
        async with async_client.dataset.with_streaming_response.retrieve_files(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as dataset:
            assert not dataset.is_closed
            assert dataset.http_request.headers.get("X-Stainless-Lang") == "python"

            assert await dataset.json() == {"foo": "bar"}
            assert cast(Any, dataset.is_closed) is True
            assert isinstance(dataset, AsyncStreamedBinaryAPIResponse)

        assert cast(Any, dataset.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_path_params_retrieve_files(self, async_client: AsyncQuark) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.dataset.with_raw_response.retrieve_files(
                id="",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve_json(self, async_client: AsyncQuark) -> None:
        dataset = await async_client.dataset.retrieve_json(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(str, dataset, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve_json_with_all_params(self, async_client: AsyncQuark) -> None:
        dataset = await async_client.dataset.retrieve_json(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            max_cell_size=0,
        )
        assert_matches_type(str, dataset, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_retrieve_json(self, async_client: AsyncQuark) -> None:
        response = await async_client.dataset.with_raw_response.retrieve_json(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        dataset = await response.parse()
        assert_matches_type(str, dataset, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_retrieve_json(self, async_client: AsyncQuark) -> None:
        async with async_client.dataset.with_streaming_response.retrieve_json(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            dataset = await response.parse()
            assert_matches_type(str, dataset, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_retrieve_json(self, async_client: AsyncQuark) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.dataset.with_raw_response.retrieve_json(
                id="",
            )
