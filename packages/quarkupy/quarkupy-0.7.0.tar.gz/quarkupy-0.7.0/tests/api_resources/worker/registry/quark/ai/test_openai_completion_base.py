# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from quarkupy import Quark, AsyncQuark
from tests.utils import assert_matches_type
from quarkupy.types.history import QuarkHistoryItem

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestOpenAICompletionBase:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_run(self, client: Quark) -> None:
        openai_completion_base = client.worker.registry.quark.ai.openai_completion_base.run(
            api_key="api_key",
            ipc_dataset_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            lattice_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(QuarkHistoryItem, openai_completion_base, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_run_with_all_params(self, client: Quark) -> None:
        openai_completion_base = client.worker.registry.quark.ai.openai_completion_base.run(
            api_key="api_key",
            ipc_dataset_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            lattice_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            opt_explode_json=True,
            opt_json_output=True,
            opt_max_output_tokens=0,
            opt_model_name="opt_model_name",
            opt_prompt_column="opt_prompt_column",
            opt_system_prompt="opt_system_prompt",
        )
        assert_matches_type(QuarkHistoryItem, openai_completion_base, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_run(self, client: Quark) -> None:
        response = client.worker.registry.quark.ai.openai_completion_base.with_raw_response.run(
            api_key="api_key",
            ipc_dataset_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            lattice_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        openai_completion_base = response.parse()
        assert_matches_type(QuarkHistoryItem, openai_completion_base, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_run(self, client: Quark) -> None:
        with client.worker.registry.quark.ai.openai_completion_base.with_streaming_response.run(
            api_key="api_key",
            ipc_dataset_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            lattice_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            openai_completion_base = response.parse()
            assert_matches_type(QuarkHistoryItem, openai_completion_base, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncOpenAICompletionBase:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_run(self, async_client: AsyncQuark) -> None:
        openai_completion_base = await async_client.worker.registry.quark.ai.openai_completion_base.run(
            api_key="api_key",
            ipc_dataset_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            lattice_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(QuarkHistoryItem, openai_completion_base, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_run_with_all_params(self, async_client: AsyncQuark) -> None:
        openai_completion_base = await async_client.worker.registry.quark.ai.openai_completion_base.run(
            api_key="api_key",
            ipc_dataset_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            lattice_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            opt_explode_json=True,
            opt_json_output=True,
            opt_max_output_tokens=0,
            opt_model_name="opt_model_name",
            opt_prompt_column="opt_prompt_column",
            opt_system_prompt="opt_system_prompt",
        )
        assert_matches_type(QuarkHistoryItem, openai_completion_base, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_run(self, async_client: AsyncQuark) -> None:
        response = await async_client.worker.registry.quark.ai.openai_completion_base.with_raw_response.run(
            api_key="api_key",
            ipc_dataset_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            lattice_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        openai_completion_base = await response.parse()
        assert_matches_type(QuarkHistoryItem, openai_completion_base, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_run(self, async_client: AsyncQuark) -> None:
        async with async_client.worker.registry.quark.ai.openai_completion_base.with_streaming_response.run(
            api_key="api_key",
            ipc_dataset_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            lattice_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            openai_completion_base = await response.parse()
            assert_matches_type(QuarkHistoryItem, openai_completion_base, path=["response"])

        assert cast(Any, response.is_closed) is True
