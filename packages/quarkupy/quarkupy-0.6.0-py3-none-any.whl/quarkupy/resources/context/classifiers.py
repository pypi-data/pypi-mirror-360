# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from datetime import datetime

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
from ...types.context import ReferenceDepth, classifier_update_params, classifier_update_partial_params
from ...types.context.classifier import Classifier
from ...types.context.reference_depth import ReferenceDepth
from ...types.context.classifier_list_response import ClassifierListResponse
from ...types.context.success_response_message import SuccessResponseMessage

__all__ = ["ClassifiersResource", "AsyncClassifiersResource"]


class ClassifiersResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ClassifiersResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/quarklabsai/quarkupy#accessing-raw-response-data-eg-headers
        """
        return ClassifiersResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ClassifiersResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/quarklabsai/quarkupy#with_streaming_response
        """
        return ClassifiersResourceWithStreamingResponse(self)

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
    ) -> Classifier:
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
            f"/context/classifiers/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Classifier,
        )

    def update(
        self,
        *,
        model_role_id: str,
        name: str,
        owned_by_identity_id: str,
        reference_depth: ReferenceDepth,
        description: str | NotGiven = NOT_GIVEN,
        parent_classifier_id: str | NotGiven = NOT_GIVEN,
        updated_at: Union[str, datetime] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Classifier:
        """
        Args:
          model_role_id: # Model Role

              Determines which model executes the classifier

          name: # Classifier Name

          owned_by_identity_id: # Owner ID

          reference_depth: # Match Segments or Sentences?

          description: # Classifier Description

              Note: the LLM uses this for matching so be descriptive

          updated_at: # Last Updated

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "application/json; charset=utf-8", **(extra_headers or {})}
        return self._put(
            "/context/classifiers",
            body=maybe_transform(
                {
                    "model_role_id": model_role_id,
                    "name": name,
                    "owned_by_identity_id": owned_by_identity_id,
                    "reference_depth": reference_depth,
                    "description": description,
                    "parent_classifier_id": parent_classifier_id,
                    "updated_at": updated_at,
                },
                classifier_update_params.ClassifierUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Classifier,
        )

    def list(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ClassifierListResponse:
        extra_headers = {"Accept": "application/json; charset=utf-8", **(extra_headers or {})}
        return self._get(
            "/context/classifiers",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ClassifierListResponse,
        )

    def delete(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SuccessResponseMessage:
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
        return self._delete(
            f"/context/classifiers/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SuccessResponseMessage,
        )

    def retrieve_schema(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        extra_headers = {"Accept": "application/json; charset=utf-8", **(extra_headers or {})}
        return self._get(
            "/context/classifiers/schema",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    def update_partial(
        self,
        id: str,
        *,
        model_role_id: str,
        name: str,
        owned_by_identity_id: str,
        reference_depth: ReferenceDepth,
        description: str | NotGiven = NOT_GIVEN,
        parent_classifier_id: str | NotGiven = NOT_GIVEN,
        updated_at: Union[str, datetime] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Classifier:
        """
        Args:
          model_role_id: # Model Role

              Determines which model executes the classifier

          name: # Classifier Name

          owned_by_identity_id: # Owner ID

          reference_depth: # Match Segments or Sentences?

          description: # Classifier Description

              Note: the LLM uses this for matching so be descriptive

          updated_at: # Last Updated

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {"Accept": "application/json; charset=utf-8", **(extra_headers or {})}
        return self._patch(
            f"/context/classifiers/{id}",
            body=maybe_transform(
                {
                    "model_role_id": model_role_id,
                    "name": name,
                    "owned_by_identity_id": owned_by_identity_id,
                    "reference_depth": reference_depth,
                    "description": description,
                    "parent_classifier_id": parent_classifier_id,
                    "updated_at": updated_at,
                },
                classifier_update_partial_params.ClassifierUpdatePartialParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Classifier,
        )


class AsyncClassifiersResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncClassifiersResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/quarklabsai/quarkupy#accessing-raw-response-data-eg-headers
        """
        return AsyncClassifiersResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncClassifiersResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/quarklabsai/quarkupy#with_streaming_response
        """
        return AsyncClassifiersResourceWithStreamingResponse(self)

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
    ) -> Classifier:
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
            f"/context/classifiers/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Classifier,
        )

    async def update(
        self,
        *,
        model_role_id: str,
        name: str,
        owned_by_identity_id: str,
        reference_depth: ReferenceDepth,
        description: str | NotGiven = NOT_GIVEN,
        parent_classifier_id: str | NotGiven = NOT_GIVEN,
        updated_at: Union[str, datetime] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Classifier:
        """
        Args:
          model_role_id: # Model Role

              Determines which model executes the classifier

          name: # Classifier Name

          owned_by_identity_id: # Owner ID

          reference_depth: # Match Segments or Sentences?

          description: # Classifier Description

              Note: the LLM uses this for matching so be descriptive

          updated_at: # Last Updated

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "application/json; charset=utf-8", **(extra_headers or {})}
        return await self._put(
            "/context/classifiers",
            body=await async_maybe_transform(
                {
                    "model_role_id": model_role_id,
                    "name": name,
                    "owned_by_identity_id": owned_by_identity_id,
                    "reference_depth": reference_depth,
                    "description": description,
                    "parent_classifier_id": parent_classifier_id,
                    "updated_at": updated_at,
                },
                classifier_update_params.ClassifierUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Classifier,
        )

    async def list(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ClassifierListResponse:
        extra_headers = {"Accept": "application/json; charset=utf-8", **(extra_headers or {})}
        return await self._get(
            "/context/classifiers",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ClassifierListResponse,
        )

    async def delete(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SuccessResponseMessage:
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
        return await self._delete(
            f"/context/classifiers/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SuccessResponseMessage,
        )

    async def retrieve_schema(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        extra_headers = {"Accept": "application/json; charset=utf-8", **(extra_headers or {})}
        return await self._get(
            "/context/classifiers/schema",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    async def update_partial(
        self,
        id: str,
        *,
        model_role_id: str,
        name: str,
        owned_by_identity_id: str,
        reference_depth: ReferenceDepth,
        description: str | NotGiven = NOT_GIVEN,
        parent_classifier_id: str | NotGiven = NOT_GIVEN,
        updated_at: Union[str, datetime] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Classifier:
        """
        Args:
          model_role_id: # Model Role

              Determines which model executes the classifier

          name: # Classifier Name

          owned_by_identity_id: # Owner ID

          reference_depth: # Match Segments or Sentences?

          description: # Classifier Description

              Note: the LLM uses this for matching so be descriptive

          updated_at: # Last Updated

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {"Accept": "application/json; charset=utf-8", **(extra_headers or {})}
        return await self._patch(
            f"/context/classifiers/{id}",
            body=await async_maybe_transform(
                {
                    "model_role_id": model_role_id,
                    "name": name,
                    "owned_by_identity_id": owned_by_identity_id,
                    "reference_depth": reference_depth,
                    "description": description,
                    "parent_classifier_id": parent_classifier_id,
                    "updated_at": updated_at,
                },
                classifier_update_partial_params.ClassifierUpdatePartialParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Classifier,
        )


class ClassifiersResourceWithRawResponse:
    def __init__(self, classifiers: ClassifiersResource) -> None:
        self._classifiers = classifiers

        self.retrieve = to_raw_response_wrapper(
            classifiers.retrieve,
        )
        self.update = to_raw_response_wrapper(
            classifiers.update,
        )
        self.list = to_raw_response_wrapper(
            classifiers.list,
        )
        self.delete = to_raw_response_wrapper(
            classifiers.delete,
        )
        self.retrieve_schema = to_raw_response_wrapper(
            classifiers.retrieve_schema,
        )
        self.update_partial = to_raw_response_wrapper(
            classifiers.update_partial,
        )


class AsyncClassifiersResourceWithRawResponse:
    def __init__(self, classifiers: AsyncClassifiersResource) -> None:
        self._classifiers = classifiers

        self.retrieve = async_to_raw_response_wrapper(
            classifiers.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            classifiers.update,
        )
        self.list = async_to_raw_response_wrapper(
            classifiers.list,
        )
        self.delete = async_to_raw_response_wrapper(
            classifiers.delete,
        )
        self.retrieve_schema = async_to_raw_response_wrapper(
            classifiers.retrieve_schema,
        )
        self.update_partial = async_to_raw_response_wrapper(
            classifiers.update_partial,
        )


class ClassifiersResourceWithStreamingResponse:
    def __init__(self, classifiers: ClassifiersResource) -> None:
        self._classifiers = classifiers

        self.retrieve = to_streamed_response_wrapper(
            classifiers.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            classifiers.update,
        )
        self.list = to_streamed_response_wrapper(
            classifiers.list,
        )
        self.delete = to_streamed_response_wrapper(
            classifiers.delete,
        )
        self.retrieve_schema = to_streamed_response_wrapper(
            classifiers.retrieve_schema,
        )
        self.update_partial = to_streamed_response_wrapper(
            classifiers.update_partial,
        )


class AsyncClassifiersResourceWithStreamingResponse:
    def __init__(self, classifiers: AsyncClassifiersResource) -> None:
        self._classifiers = classifiers

        self.retrieve = async_to_streamed_response_wrapper(
            classifiers.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            classifiers.update,
        )
        self.list = async_to_streamed_response_wrapper(
            classifiers.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            classifiers.delete,
        )
        self.retrieve_schema = async_to_streamed_response_wrapper(
            classifiers.retrieve_schema,
        )
        self.update_partial = async_to_streamed_response_wrapper(
            classifiers.update_partial,
        )
