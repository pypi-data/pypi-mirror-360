# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from quarkupy import Quark, AsyncQuark
from tests.utils import assert_matches_type
from quarkupy.types import Source
from quarkupy.types.worker import (
    SourceRetrieveListResponse,
)
from quarkupy.types.context import SuccessResponseMessage

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestSource:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create(self, client: Quark) -> None:
        source = client.worker.source.create(
            config={
                "access_key_id": "access_key_id",
                "endpoint": "endpoint",
                "region": "region",
                "secret_access_key": "secret_access_key",
                "url": "url",
            },
            name="name",
        )
        assert_matches_type(Source, source, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create_with_all_params(self, client: Quark) -> None:
        source = client.worker.source.create(
            config={
                "access_key_id": "access_key_id",
                "endpoint": "endpoint",
                "region": "region",
                "secret_access_key": "secret_access_key",
                "url": "url",
            },
            name="name",
            description="description",
        )
        assert_matches_type(Source, source, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_create(self, client: Quark) -> None:
        response = client.worker.source.with_raw_response.create(
            config={
                "access_key_id": "access_key_id",
                "endpoint": "endpoint",
                "region": "region",
                "secret_access_key": "secret_access_key",
                "url": "url",
            },
            name="name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        source = response.parse()
        assert_matches_type(Source, source, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_create(self, client: Quark) -> None:
        with client.worker.source.with_streaming_response.create(
            config={
                "access_key_id": "access_key_id",
                "endpoint": "endpoint",
                "region": "region",
                "secret_access_key": "secret_access_key",
                "url": "url",
            },
            name="name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            source = response.parse()
            assert_matches_type(Source, source, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve(self, client: Quark) -> None:
        source = client.worker.source.retrieve(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(Source, source, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_retrieve(self, client: Quark) -> None:
        response = client.worker.source.with_raw_response.retrieve(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        source = response.parse()
        assert_matches_type(Source, source, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_retrieve(self, client: Quark) -> None:
        with client.worker.source.with_streaming_response.retrieve(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            source = response.parse()
            assert_matches_type(Source, source, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_retrieve(self, client: Quark) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.worker.source.with_raw_response.retrieve(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_list(self, client: Quark) -> None:
        source = client.worker.source.list()
        assert_matches_type(SuccessResponseMessage, source, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_list(self, client: Quark) -> None:
        response = client.worker.source.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        source = response.parse()
        assert_matches_type(SuccessResponseMessage, source, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_list(self, client: Quark) -> None:
        with client.worker.source.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            source = response.parse()
            assert_matches_type(SuccessResponseMessage, source, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve_add_all(self, client: Quark) -> None:
        source = client.worker.source.retrieve_add_all(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(SuccessResponseMessage, source, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve_add_all_with_all_params(self, client: Quark) -> None:
        source = client.worker.source.retrieve_add_all(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            path="path",
        )
        assert_matches_type(SuccessResponseMessage, source, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_retrieve_add_all(self, client: Quark) -> None:
        response = client.worker.source.with_raw_response.retrieve_add_all(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        source = response.parse()
        assert_matches_type(SuccessResponseMessage, source, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_retrieve_add_all(self, client: Quark) -> None:
        with client.worker.source.with_streaming_response.retrieve_add_all(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            source = response.parse()
            assert_matches_type(SuccessResponseMessage, source, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_retrieve_add_all(self, client: Quark) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.worker.source.with_raw_response.retrieve_add_all(
                id="",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve_list(self, client: Quark) -> None:
        source = client.worker.source.retrieve_list(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(SourceRetrieveListResponse, source, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve_list_with_all_params(self, client: Quark) -> None:
        source = client.worker.source.retrieve_list(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            path="path",
        )
        assert_matches_type(SourceRetrieveListResponse, source, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_retrieve_list(self, client: Quark) -> None:
        response = client.worker.source.with_raw_response.retrieve_list(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        source = response.parse()
        assert_matches_type(SourceRetrieveListResponse, source, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_retrieve_list(self, client: Quark) -> None:
        with client.worker.source.with_streaming_response.retrieve_list(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            source = response.parse()
            assert_matches_type(SourceRetrieveListResponse, source, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_retrieve_list(self, client: Quark) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.worker.source.with_raw_response.retrieve_list(
                id="",
            )


class TestAsyncSource:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_create(self, async_client: AsyncQuark) -> None:
        source = await async_client.worker.source.create(
            config={
                "access_key_id": "access_key_id",
                "endpoint": "endpoint",
                "region": "region",
                "secret_access_key": "secret_access_key",
                "url": "url",
            },
            name="name",
        )
        assert_matches_type(Source, source, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncQuark) -> None:
        source = await async_client.worker.source.create(
            config={
                "access_key_id": "access_key_id",
                "endpoint": "endpoint",
                "region": "region",
                "secret_access_key": "secret_access_key",
                "url": "url",
            },
            name="name",
            description="description",
        )
        assert_matches_type(Source, source, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncQuark) -> None:
        response = await async_client.worker.source.with_raw_response.create(
            config={
                "access_key_id": "access_key_id",
                "endpoint": "endpoint",
                "region": "region",
                "secret_access_key": "secret_access_key",
                "url": "url",
            },
            name="name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        source = await response.parse()
        assert_matches_type(Source, source, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncQuark) -> None:
        async with async_client.worker.source.with_streaming_response.create(
            config={
                "access_key_id": "access_key_id",
                "endpoint": "endpoint",
                "region": "region",
                "secret_access_key": "secret_access_key",
                "url": "url",
            },
            name="name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            source = await response.parse()
            assert_matches_type(Source, source, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncQuark) -> None:
        source = await async_client.worker.source.retrieve(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(Source, source, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncQuark) -> None:
        response = await async_client.worker.source.with_raw_response.retrieve(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        source = await response.parse()
        assert_matches_type(Source, source, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncQuark) -> None:
        async with async_client.worker.source.with_streaming_response.retrieve(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            source = await response.parse()
            assert_matches_type(Source, source, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncQuark) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.worker.source.with_raw_response.retrieve(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_list(self, async_client: AsyncQuark) -> None:
        source = await async_client.worker.source.list()
        assert_matches_type(SuccessResponseMessage, source, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncQuark) -> None:
        response = await async_client.worker.source.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        source = await response.parse()
        assert_matches_type(SuccessResponseMessage, source, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncQuark) -> None:
        async with async_client.worker.source.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            source = await response.parse()
            assert_matches_type(SuccessResponseMessage, source, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve_add_all(self, async_client: AsyncQuark) -> None:
        source = await async_client.worker.source.retrieve_add_all(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(SuccessResponseMessage, source, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve_add_all_with_all_params(self, async_client: AsyncQuark) -> None:
        source = await async_client.worker.source.retrieve_add_all(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            path="path",
        )
        assert_matches_type(SuccessResponseMessage, source, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_retrieve_add_all(self, async_client: AsyncQuark) -> None:
        response = await async_client.worker.source.with_raw_response.retrieve_add_all(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        source = await response.parse()
        assert_matches_type(SuccessResponseMessage, source, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_retrieve_add_all(self, async_client: AsyncQuark) -> None:
        async with async_client.worker.source.with_streaming_response.retrieve_add_all(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            source = await response.parse()
            assert_matches_type(SuccessResponseMessage, source, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_retrieve_add_all(self, async_client: AsyncQuark) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.worker.source.with_raw_response.retrieve_add_all(
                id="",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve_list(self, async_client: AsyncQuark) -> None:
        source = await async_client.worker.source.retrieve_list(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(SourceRetrieveListResponse, source, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve_list_with_all_params(self, async_client: AsyncQuark) -> None:
        source = await async_client.worker.source.retrieve_list(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            path="path",
        )
        assert_matches_type(SourceRetrieveListResponse, source, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_retrieve_list(self, async_client: AsyncQuark) -> None:
        response = await async_client.worker.source.with_raw_response.retrieve_list(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        source = await response.parse()
        assert_matches_type(SourceRetrieveListResponse, source, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_retrieve_list(self, async_client: AsyncQuark) -> None:
        async with async_client.worker.source.with_streaming_response.retrieve_list(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            source = await response.parse()
            assert_matches_type(SourceRetrieveListResponse, source, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_retrieve_list(self, async_client: AsyncQuark) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.worker.source.with_raw_response.retrieve_list(
                id="",
            )
