# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from quarkupy import Quark, AsyncQuark
from tests.utils import assert_matches_type
from quarkupy._utils import parse_datetime
from quarkupy.types.history import QuarkHistoryItem

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestQuark:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve(self, client: Quark) -> None:
        quark = client.history.quark.retrieve(
            "id",
        )
        assert_matches_type(QuarkHistoryItem, quark, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_retrieve(self, client: Quark) -> None:
        response = client.history.quark.with_raw_response.retrieve(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        quark = response.parse()
        assert_matches_type(QuarkHistoryItem, quark, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_retrieve(self, client: Quark) -> None:
        with client.history.quark.with_streaming_response.retrieve(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            quark = response.parse()
            assert_matches_type(QuarkHistoryItem, quark, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_retrieve(self, client: Quark) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.history.quark.with_raw_response.retrieve(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_update(self, client: Quark) -> None:
        quark = client.history.quark.update(
            created_at=parse_datetime("2019-12-27T18:11:19.117Z"),
            flow_history_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            identity_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            input={},
            output={},
            quark_history_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            registry_qrn="registry_qrn",
            state={},
            status="New",
        )
        assert_matches_type(QuarkHistoryItem, quark, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_update_with_all_params(self, client: Quark) -> None:
        quark = client.history.quark.update(
            created_at=parse_datetime("2019-12-27T18:11:19.117Z"),
            flow_history_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            identity_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            input={},
            output={},
            quark_history_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            registry_qrn="registry_qrn",
            state={},
            status="New",
            registry_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            runner_task_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            supervisor_task_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            worker_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(QuarkHistoryItem, quark, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_update(self, client: Quark) -> None:
        response = client.history.quark.with_raw_response.update(
            created_at=parse_datetime("2019-12-27T18:11:19.117Z"),
            flow_history_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            identity_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            input={},
            output={},
            quark_history_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            registry_qrn="registry_qrn",
            state={},
            status="New",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        quark = response.parse()
        assert_matches_type(QuarkHistoryItem, quark, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_update(self, client: Quark) -> None:
        with client.history.quark.with_streaming_response.update(
            created_at=parse_datetime("2019-12-27T18:11:19.117Z"),
            flow_history_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            identity_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            input={},
            output={},
            quark_history_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            registry_qrn="registry_qrn",
            state={},
            status="New",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            quark = response.parse()
            assert_matches_type(QuarkHistoryItem, quark, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncQuark:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncQuark) -> None:
        quark = await async_client.history.quark.retrieve(
            "id",
        )
        assert_matches_type(QuarkHistoryItem, quark, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncQuark) -> None:
        response = await async_client.history.quark.with_raw_response.retrieve(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        quark = await response.parse()
        assert_matches_type(QuarkHistoryItem, quark, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncQuark) -> None:
        async with async_client.history.quark.with_streaming_response.retrieve(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            quark = await response.parse()
            assert_matches_type(QuarkHistoryItem, quark, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncQuark) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.history.quark.with_raw_response.retrieve(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_update(self, async_client: AsyncQuark) -> None:
        quark = await async_client.history.quark.update(
            created_at=parse_datetime("2019-12-27T18:11:19.117Z"),
            flow_history_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            identity_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            input={},
            output={},
            quark_history_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            registry_qrn="registry_qrn",
            state={},
            status="New",
        )
        assert_matches_type(QuarkHistoryItem, quark, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncQuark) -> None:
        quark = await async_client.history.quark.update(
            created_at=parse_datetime("2019-12-27T18:11:19.117Z"),
            flow_history_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            identity_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            input={},
            output={},
            quark_history_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            registry_qrn="registry_qrn",
            state={},
            status="New",
            registry_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            runner_task_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            supervisor_task_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            worker_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(QuarkHistoryItem, quark, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncQuark) -> None:
        response = await async_client.history.quark.with_raw_response.update(
            created_at=parse_datetime("2019-12-27T18:11:19.117Z"),
            flow_history_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            identity_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            input={},
            output={},
            quark_history_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            registry_qrn="registry_qrn",
            state={},
            status="New",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        quark = await response.parse()
        assert_matches_type(QuarkHistoryItem, quark, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncQuark) -> None:
        async with async_client.history.quark.with_streaming_response.update(
            created_at=parse_datetime("2019-12-27T18:11:19.117Z"),
            flow_history_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            identity_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            input={},
            output={},
            quark_history_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            registry_qrn="registry_qrn",
            state={},
            status="New",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            quark = await response.parse()
            assert_matches_type(QuarkHistoryItem, quark, path=["response"])

        assert cast(Any, response.is_closed) is True
