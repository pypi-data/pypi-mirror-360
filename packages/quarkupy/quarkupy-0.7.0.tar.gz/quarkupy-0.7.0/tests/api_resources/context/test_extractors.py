# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from quarkupy import Quark, AsyncQuark
from tests.utils import assert_matches_type
from quarkupy._utils import parse_datetime
from quarkupy.types.context import (
    Extractor,
    ExtractorListResponse,
    SuccessResponseMessage,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestExtractors:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve(self, client: Quark) -> None:
        extractor = client.context.extractors.retrieve(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(Extractor, extractor, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_retrieve(self, client: Quark) -> None:
        response = client.context.extractors.with_raw_response.retrieve(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        extractor = response.parse()
        assert_matches_type(Extractor, extractor, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_retrieve(self, client: Quark) -> None:
        with client.context.extractors.with_streaming_response.retrieve(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            extractor = response.parse()
            assert_matches_type(Extractor, extractor, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_retrieve(self, client: Quark) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.context.extractors.with_raw_response.retrieve(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_update(self, client: Quark) -> None:
        extractor = client.context.extractors.update(
            data_type="String",
            model_role_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            name="name",
            owned_by_identity_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            reference_depth="Segment",
        )
        assert_matches_type(Extractor, extractor, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_update_with_all_params(self, client: Quark) -> None:
        extractor = client.context.extractors.update(
            data_type="String",
            model_role_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            name="name",
            owned_by_identity_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            reference_depth="Segment",
            add_reason=True,
            add_references=True,
            config={},
            description="description",
            examples={},
            updated_at=parse_datetime("2019-12-27T18:11:19.117Z"),
        )
        assert_matches_type(Extractor, extractor, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_update(self, client: Quark) -> None:
        response = client.context.extractors.with_raw_response.update(
            data_type="String",
            model_role_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            name="name",
            owned_by_identity_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            reference_depth="Segment",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        extractor = response.parse()
        assert_matches_type(Extractor, extractor, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_update(self, client: Quark) -> None:
        with client.context.extractors.with_streaming_response.update(
            data_type="String",
            model_role_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            name="name",
            owned_by_identity_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            reference_depth="Segment",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            extractor = response.parse()
            assert_matches_type(Extractor, extractor, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_list(self, client: Quark) -> None:
        extractor = client.context.extractors.list()
        assert_matches_type(ExtractorListResponse, extractor, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_list(self, client: Quark) -> None:
        response = client.context.extractors.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        extractor = response.parse()
        assert_matches_type(ExtractorListResponse, extractor, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_list(self, client: Quark) -> None:
        with client.context.extractors.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            extractor = response.parse()
            assert_matches_type(ExtractorListResponse, extractor, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_delete(self, client: Quark) -> None:
        extractor = client.context.extractors.delete(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(SuccessResponseMessage, extractor, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_delete(self, client: Quark) -> None:
        response = client.context.extractors.with_raw_response.delete(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        extractor = response.parse()
        assert_matches_type(SuccessResponseMessage, extractor, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_delete(self, client: Quark) -> None:
        with client.context.extractors.with_streaming_response.delete(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            extractor = response.parse()
            assert_matches_type(SuccessResponseMessage, extractor, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_delete(self, client: Quark) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.context.extractors.with_raw_response.delete(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve_schema(self, client: Quark) -> None:
        extractor = client.context.extractors.retrieve_schema()
        assert_matches_type(object, extractor, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_retrieve_schema(self, client: Quark) -> None:
        response = client.context.extractors.with_raw_response.retrieve_schema()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        extractor = response.parse()
        assert_matches_type(object, extractor, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_retrieve_schema(self, client: Quark) -> None:
        with client.context.extractors.with_streaming_response.retrieve_schema() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            extractor = response.parse()
            assert_matches_type(object, extractor, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_update_partial(self, client: Quark) -> None:
        extractor = client.context.extractors.update_partial(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            data_type="String",
            model_role_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            name="name",
            owned_by_identity_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            reference_depth="Segment",
        )
        assert_matches_type(Extractor, extractor, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_update_partial_with_all_params(self, client: Quark) -> None:
        extractor = client.context.extractors.update_partial(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            data_type="String",
            model_role_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            name="name",
            owned_by_identity_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            reference_depth="Segment",
            add_reason=True,
            add_references=True,
            config={},
            description="description",
            examples={},
            updated_at=parse_datetime("2019-12-27T18:11:19.117Z"),
        )
        assert_matches_type(Extractor, extractor, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_update_partial(self, client: Quark) -> None:
        response = client.context.extractors.with_raw_response.update_partial(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            data_type="String",
            model_role_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            name="name",
            owned_by_identity_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            reference_depth="Segment",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        extractor = response.parse()
        assert_matches_type(Extractor, extractor, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_update_partial(self, client: Quark) -> None:
        with client.context.extractors.with_streaming_response.update_partial(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            data_type="String",
            model_role_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            name="name",
            owned_by_identity_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            reference_depth="Segment",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            extractor = response.parse()
            assert_matches_type(Extractor, extractor, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_update_partial(self, client: Quark) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.context.extractors.with_raw_response.update_partial(
                id="",
                data_type="String",
                model_role_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                name="name",
                owned_by_identity_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                reference_depth="Segment",
            )


class TestAsyncExtractors:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncQuark) -> None:
        extractor = await async_client.context.extractors.retrieve(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(Extractor, extractor, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncQuark) -> None:
        response = await async_client.context.extractors.with_raw_response.retrieve(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        extractor = await response.parse()
        assert_matches_type(Extractor, extractor, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncQuark) -> None:
        async with async_client.context.extractors.with_streaming_response.retrieve(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            extractor = await response.parse()
            assert_matches_type(Extractor, extractor, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncQuark) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.context.extractors.with_raw_response.retrieve(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_update(self, async_client: AsyncQuark) -> None:
        extractor = await async_client.context.extractors.update(
            data_type="String",
            model_role_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            name="name",
            owned_by_identity_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            reference_depth="Segment",
        )
        assert_matches_type(Extractor, extractor, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncQuark) -> None:
        extractor = await async_client.context.extractors.update(
            data_type="String",
            model_role_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            name="name",
            owned_by_identity_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            reference_depth="Segment",
            add_reason=True,
            add_references=True,
            config={},
            description="description",
            examples={},
            updated_at=parse_datetime("2019-12-27T18:11:19.117Z"),
        )
        assert_matches_type(Extractor, extractor, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncQuark) -> None:
        response = await async_client.context.extractors.with_raw_response.update(
            data_type="String",
            model_role_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            name="name",
            owned_by_identity_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            reference_depth="Segment",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        extractor = await response.parse()
        assert_matches_type(Extractor, extractor, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncQuark) -> None:
        async with async_client.context.extractors.with_streaming_response.update(
            data_type="String",
            model_role_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            name="name",
            owned_by_identity_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            reference_depth="Segment",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            extractor = await response.parse()
            assert_matches_type(Extractor, extractor, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_list(self, async_client: AsyncQuark) -> None:
        extractor = await async_client.context.extractors.list()
        assert_matches_type(ExtractorListResponse, extractor, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncQuark) -> None:
        response = await async_client.context.extractors.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        extractor = await response.parse()
        assert_matches_type(ExtractorListResponse, extractor, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncQuark) -> None:
        async with async_client.context.extractors.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            extractor = await response.parse()
            assert_matches_type(ExtractorListResponse, extractor, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_delete(self, async_client: AsyncQuark) -> None:
        extractor = await async_client.context.extractors.delete(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(SuccessResponseMessage, extractor, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncQuark) -> None:
        response = await async_client.context.extractors.with_raw_response.delete(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        extractor = await response.parse()
        assert_matches_type(SuccessResponseMessage, extractor, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncQuark) -> None:
        async with async_client.context.extractors.with_streaming_response.delete(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            extractor = await response.parse()
            assert_matches_type(SuccessResponseMessage, extractor, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncQuark) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.context.extractors.with_raw_response.delete(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve_schema(self, async_client: AsyncQuark) -> None:
        extractor = await async_client.context.extractors.retrieve_schema()
        assert_matches_type(object, extractor, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_retrieve_schema(self, async_client: AsyncQuark) -> None:
        response = await async_client.context.extractors.with_raw_response.retrieve_schema()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        extractor = await response.parse()
        assert_matches_type(object, extractor, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_retrieve_schema(self, async_client: AsyncQuark) -> None:
        async with async_client.context.extractors.with_streaming_response.retrieve_schema() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            extractor = await response.parse()
            assert_matches_type(object, extractor, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_update_partial(self, async_client: AsyncQuark) -> None:
        extractor = await async_client.context.extractors.update_partial(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            data_type="String",
            model_role_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            name="name",
            owned_by_identity_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            reference_depth="Segment",
        )
        assert_matches_type(Extractor, extractor, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_update_partial_with_all_params(self, async_client: AsyncQuark) -> None:
        extractor = await async_client.context.extractors.update_partial(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            data_type="String",
            model_role_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            name="name",
            owned_by_identity_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            reference_depth="Segment",
            add_reason=True,
            add_references=True,
            config={},
            description="description",
            examples={},
            updated_at=parse_datetime("2019-12-27T18:11:19.117Z"),
        )
        assert_matches_type(Extractor, extractor, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_update_partial(self, async_client: AsyncQuark) -> None:
        response = await async_client.context.extractors.with_raw_response.update_partial(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            data_type="String",
            model_role_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            name="name",
            owned_by_identity_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            reference_depth="Segment",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        extractor = await response.parse()
        assert_matches_type(Extractor, extractor, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_update_partial(self, async_client: AsyncQuark) -> None:
        async with async_client.context.extractors.with_streaming_response.update_partial(
            id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            data_type="String",
            model_role_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            name="name",
            owned_by_identity_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            reference_depth="Segment",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            extractor = await response.parse()
            assert_matches_type(Extractor, extractor, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_update_partial(self, async_client: AsyncQuark) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.context.extractors.with_raw_response.update_partial(
                id="",
                data_type="String",
                model_role_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                name="name",
                owned_by_identity_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                reference_depth="Segment",
            )
