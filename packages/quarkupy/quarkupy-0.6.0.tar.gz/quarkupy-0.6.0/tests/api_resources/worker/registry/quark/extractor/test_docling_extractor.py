# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from quarkupy import Quark, AsyncQuark
from tests.utils import assert_matches_type
from quarkupy.types.history import QuarkHistoryItem

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestDoclingExtractor:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_run(self, client: Quark) -> None:
        docling_extractor = client.worker.registry.quark.extractor.docling_extractor.run(
            ipc_dataset_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            lattice_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(QuarkHistoryItem, docling_extractor, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_run_with_all_params(self, client: Quark) -> None:
        docling_extractor = client.worker.registry.quark.extractor.docling_extractor.run(
            ipc_dataset_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            lattice_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            opt_device="opt_device",
            opt_do_cell_matching=True,
            opt_do_ocr=True,
            opt_do_table_structure=True,
            opt_generate_page_images=True,
            opt_generate_picture_images=True,
            opt_image_resolution_scale=0,
            opt_input_file_types=["AsciiDoc"],
            opt_max_file_size=0,
            opt_max_pages=0,
            opt_output_type="DocTags",
            opt_use_gpu=True,
        )
        assert_matches_type(QuarkHistoryItem, docling_extractor, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_run(self, client: Quark) -> None:
        response = client.worker.registry.quark.extractor.docling_extractor.with_raw_response.run(
            ipc_dataset_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            lattice_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        docling_extractor = response.parse()
        assert_matches_type(QuarkHistoryItem, docling_extractor, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_run(self, client: Quark) -> None:
        with client.worker.registry.quark.extractor.docling_extractor.with_streaming_response.run(
            ipc_dataset_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            lattice_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            docling_extractor = response.parse()
            assert_matches_type(QuarkHistoryItem, docling_extractor, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncDoclingExtractor:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_run(self, async_client: AsyncQuark) -> None:
        docling_extractor = await async_client.worker.registry.quark.extractor.docling_extractor.run(
            ipc_dataset_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            lattice_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(QuarkHistoryItem, docling_extractor, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_run_with_all_params(self, async_client: AsyncQuark) -> None:
        docling_extractor = await async_client.worker.registry.quark.extractor.docling_extractor.run(
            ipc_dataset_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            lattice_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            opt_device="opt_device",
            opt_do_cell_matching=True,
            opt_do_ocr=True,
            opt_do_table_structure=True,
            opt_generate_page_images=True,
            opt_generate_picture_images=True,
            opt_image_resolution_scale=0,
            opt_input_file_types=["AsciiDoc"],
            opt_max_file_size=0,
            opt_max_pages=0,
            opt_output_type="DocTags",
            opt_use_gpu=True,
        )
        assert_matches_type(QuarkHistoryItem, docling_extractor, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_run(self, async_client: AsyncQuark) -> None:
        response = await async_client.worker.registry.quark.extractor.docling_extractor.with_raw_response.run(
            ipc_dataset_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            lattice_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        docling_extractor = await response.parse()
        assert_matches_type(QuarkHistoryItem, docling_extractor, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_run(self, async_client: AsyncQuark) -> None:
        async with async_client.worker.registry.quark.extractor.docling_extractor.with_streaming_response.run(
            ipc_dataset_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            lattice_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            docling_extractor = await response.parse()
            assert_matches_type(QuarkHistoryItem, docling_extractor, path=["response"])

        assert cast(Any, response.is_closed) is True
