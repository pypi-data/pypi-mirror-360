# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from quarkupy import Quark, AsyncQuark
from tests.utils import assert_matches_type
from quarkupy.types.history import QuarkHistoryItem

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestHandlebarsBase:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_run(self, client: Quark) -> None:
        handlebars_base = client.worker.registry.quark.transformer.handlebars_base.run(
            input_columns=["string"],
            ipc_dataset_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            lattice_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            template="template",
        )
        assert_matches_type(QuarkHistoryItem, handlebars_base, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_run_with_all_params(self, client: Quark) -> None:
        handlebars_base = client.worker.registry.quark.transformer.handlebars_base.run(
            input_columns=["string"],
            ipc_dataset_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            lattice_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            template="template",
            opt_rendered_col="opt_rendered_col",
        )
        assert_matches_type(QuarkHistoryItem, handlebars_base, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_run(self, client: Quark) -> None:
        response = client.worker.registry.quark.transformer.handlebars_base.with_raw_response.run(
            input_columns=["string"],
            ipc_dataset_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            lattice_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            template="template",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        handlebars_base = response.parse()
        assert_matches_type(QuarkHistoryItem, handlebars_base, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_run(self, client: Quark) -> None:
        with client.worker.registry.quark.transformer.handlebars_base.with_streaming_response.run(
            input_columns=["string"],
            ipc_dataset_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            lattice_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            template="template",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            handlebars_base = response.parse()
            assert_matches_type(QuarkHistoryItem, handlebars_base, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncHandlebarsBase:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_run(self, async_client: AsyncQuark) -> None:
        handlebars_base = await async_client.worker.registry.quark.transformer.handlebars_base.run(
            input_columns=["string"],
            ipc_dataset_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            lattice_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            template="template",
        )
        assert_matches_type(QuarkHistoryItem, handlebars_base, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_run_with_all_params(self, async_client: AsyncQuark) -> None:
        handlebars_base = await async_client.worker.registry.quark.transformer.handlebars_base.run(
            input_columns=["string"],
            ipc_dataset_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            lattice_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            template="template",
            opt_rendered_col="opt_rendered_col",
        )
        assert_matches_type(QuarkHistoryItem, handlebars_base, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_run(self, async_client: AsyncQuark) -> None:
        response = await async_client.worker.registry.quark.transformer.handlebars_base.with_raw_response.run(
            input_columns=["string"],
            ipc_dataset_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            lattice_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            template="template",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        handlebars_base = await response.parse()
        assert_matches_type(QuarkHistoryItem, handlebars_base, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_run(self, async_client: AsyncQuark) -> None:
        async with async_client.worker.registry.quark.transformer.handlebars_base.with_streaming_response.run(
            input_columns=["string"],
            ipc_dataset_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            lattice_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            template="template",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            handlebars_base = await response.parse()
            assert_matches_type(QuarkHistoryItem, handlebars_base, path=["response"])

        assert cast(Any, response.is_closed) is True
