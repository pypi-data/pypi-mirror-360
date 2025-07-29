# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from datetime import datetime
from typing_extensions import Literal

import httpx

from ..._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ..._utils import maybe_transform, async_maybe_transform
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ..._base_client import make_request_options
from ...types.history import quark_update_params
from ...types.history.quark_history_item import QuarkHistoryItem

__all__ = ["QuarkResource", "AsyncQuarkResource"]


class QuarkResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> QuarkResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/quarklabsai/quarkupy#accessing-raw-response-data-eg-headers
        """
        return QuarkResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> QuarkResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/quarklabsai/quarkupy#with_streaming_response
        """
        return QuarkResourceWithStreamingResponse(self)

    def retrieve(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> QuarkHistoryItem:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {"Accept": "application/json; charset=utf-8", **(extra_headers or {})}
        return self._get(
            f"/history/quark/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=QuarkHistoryItem,
        )

    def update(
        self,
        *,
        created_at: Union[str, datetime],
        flow_history_id: str,
        identity_id: str,
        input: object,
        output: object,
        quark_history_id: str,
        registry_qrn: str,
        state: object,
        status: Literal["New", "Scheduled", "Running", "OutputStaged", "Completed", "Failed"],
        registry_id: str | NotGiven = NOT_GIVEN,
        runner_task_id: str | NotGiven = NOT_GIVEN,
        supervisor_task_id: str | NotGiven = NOT_GIVEN,
        worker_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> QuarkHistoryItem:
        """
        Args:
          created_at: The timestamp indicating when the Quark was created.

          flow_history_id: Identifier of the associated Flow.

          identity_id: Identity of Quark runner

          input: Input data associated with the Quark, stored as a JSON value.

          output: Output data produced by the Quark execution, stored as a JSON value.

          quark_history_id: Unique identifier for the Quark.

          registry_qrn: User-facing fully qualified identifier for the registry where the Quark is
              defined.

          state: Quark State

          status: Represents the status/stage of a Quark instance

          registry_id: Registry ID of the database entry

          runner_task_id: Runner [WorkerTask] id Optional, as there are stages when no runner is assigned

          supervisor_task_id: Supervisor [WorkerTask] id Optional, as there are stages when no supervisor is
              assigned

          worker_id: Runner [WorkerTask] id Optional, as there are stages when no worker is assigned

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "application/json; charset=utf-8", **(extra_headers or {})}
        return self._put(
            "/history/quark",
            body=maybe_transform(
                {
                    "created_at": created_at,
                    "flow_history_id": flow_history_id,
                    "identity_id": identity_id,
                    "input": input,
                    "output": output,
                    "quark_history_id": quark_history_id,
                    "registry_qrn": registry_qrn,
                    "state": state,
                    "status": status,
                    "registry_id": registry_id,
                    "runner_task_id": runner_task_id,
                    "supervisor_task_id": supervisor_task_id,
                    "worker_id": worker_id,
                },
                quark_update_params.QuarkUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=QuarkHistoryItem,
        )


class AsyncQuarkResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncQuarkResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/quarklabsai/quarkupy#accessing-raw-response-data-eg-headers
        """
        return AsyncQuarkResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncQuarkResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/quarklabsai/quarkupy#with_streaming_response
        """
        return AsyncQuarkResourceWithStreamingResponse(self)

    async def retrieve(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> QuarkHistoryItem:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {"Accept": "application/json; charset=utf-8", **(extra_headers or {})}
        return await self._get(
            f"/history/quark/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=QuarkHistoryItem,
        )

    async def update(
        self,
        *,
        created_at: Union[str, datetime],
        flow_history_id: str,
        identity_id: str,
        input: object,
        output: object,
        quark_history_id: str,
        registry_qrn: str,
        state: object,
        status: Literal["New", "Scheduled", "Running", "OutputStaged", "Completed", "Failed"],
        registry_id: str | NotGiven = NOT_GIVEN,
        runner_task_id: str | NotGiven = NOT_GIVEN,
        supervisor_task_id: str | NotGiven = NOT_GIVEN,
        worker_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> QuarkHistoryItem:
        """
        Args:
          created_at: The timestamp indicating when the Quark was created.

          flow_history_id: Identifier of the associated Flow.

          identity_id: Identity of Quark runner

          input: Input data associated with the Quark, stored as a JSON value.

          output: Output data produced by the Quark execution, stored as a JSON value.

          quark_history_id: Unique identifier for the Quark.

          registry_qrn: User-facing fully qualified identifier for the registry where the Quark is
              defined.

          state: Quark State

          status: Represents the status/stage of a Quark instance

          registry_id: Registry ID of the database entry

          runner_task_id: Runner [WorkerTask] id Optional, as there are stages when no runner is assigned

          supervisor_task_id: Supervisor [WorkerTask] id Optional, as there are stages when no supervisor is
              assigned

          worker_id: Runner [WorkerTask] id Optional, as there are stages when no worker is assigned

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "application/json; charset=utf-8", **(extra_headers or {})}
        return await self._put(
            "/history/quark",
            body=await async_maybe_transform(
                {
                    "created_at": created_at,
                    "flow_history_id": flow_history_id,
                    "identity_id": identity_id,
                    "input": input,
                    "output": output,
                    "quark_history_id": quark_history_id,
                    "registry_qrn": registry_qrn,
                    "state": state,
                    "status": status,
                    "registry_id": registry_id,
                    "runner_task_id": runner_task_id,
                    "supervisor_task_id": supervisor_task_id,
                    "worker_id": worker_id,
                },
                quark_update_params.QuarkUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=QuarkHistoryItem,
        )


class QuarkResourceWithRawResponse:
    def __init__(self, quark: QuarkResource) -> None:
        self._quark = quark

        self.retrieve = to_raw_response_wrapper(
            quark.retrieve,
        )
        self.update = to_raw_response_wrapper(
            quark.update,
        )


class AsyncQuarkResourceWithRawResponse:
    def __init__(self, quark: AsyncQuarkResource) -> None:
        self._quark = quark

        self.retrieve = async_to_raw_response_wrapper(
            quark.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            quark.update,
        )


class QuarkResourceWithStreamingResponse:
    def __init__(self, quark: QuarkResource) -> None:
        self._quark = quark

        self.retrieve = to_streamed_response_wrapper(
            quark.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            quark.update,
        )


class AsyncQuarkResourceWithStreamingResponse:
    def __init__(self, quark: AsyncQuarkResource) -> None:
        self._quark = quark

        self.retrieve = async_to_streamed_response_wrapper(
            quark.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            quark.update,
        )
