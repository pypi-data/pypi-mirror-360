# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, Union, Mapping
from typing_extensions import Self, override

import httpx

from . import _exceptions
from ._qs import Querystring
from ._types import (
    NOT_GIVEN,
    Body,
    Omit,
    Query,
    Headers,
    Timeout,
    NotGiven,
    Transport,
    ProxiesTypes,
    RequestOptions,
)
from ._utils import is_given, get_async_library
from ._version import __version__
from ._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .resources import users, dataset, sources, authorize, json_schemas
from ._streaming import Stream as Stream, AsyncStream as AsyncStream
from ._exceptions import QuarkError, APIStatusError
from ._base_client import (
    DEFAULT_MAX_RETRIES,
    SyncAPIClient,
    AsyncAPIClient,
    make_request_options,
)
from .resources.admin import admin
from .resources.models import models
from .resources.worker import worker
from .resources.context import context
from .resources.history import history
from .resources.profile import profile

__all__ = ["Timeout", "Transport", "ProxiesTypes", "RequestOptions", "Quark", "AsyncQuark", "Client", "AsyncClient"]


class Quark(SyncAPIClient):
    context: context.ContextResource
    admin: admin.AdminResource
    models: models.ModelsResource
    authorize: authorize.AuthorizeResource
    profile: profile.ProfileResource
    sources: sources.SourcesResource
    users: users.UsersResource
    json_schemas: json_schemas.JsonSchemasResource
    history: history.HistoryResource
    dataset: dataset.DatasetResource
    worker: worker.WorkerResource
    with_raw_response: QuarkWithRawResponse
    with_streaming_response: QuarkWithStreamedResponse

    # client options
    api_key: str
    cookie: str | None

    def __init__(
        self,
        *,
        api_key: str | None = None,
        cookie: str | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: Union[float, Timeout, None, NotGiven] = NOT_GIVEN,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        # Configure a custom httpx client.
        # We provide a `DefaultHttpxClient` class that you can pass to retain the default values we use for `limits`, `timeout` & `follow_redirects`.
        # See the [httpx documentation](https://www.python-httpx.org/api/#client) for more details.
        http_client: httpx.Client | None = None,
        # Enable or disable schema validation for data returned by the API.
        # When enabled an error APIResponseValidationError is raised
        # if the API responds with invalid data for the expected schema.
        #
        # This parameter may be removed or changed in the future.
        # If you rely on this feature, please open a GitHub issue
        # outlining your use-case to help us decide if it should be
        # part of our public interface in the future.
        _strict_response_validation: bool = False,
    ) -> None:
        """Construct a new synchronous Quark client instance.

        This automatically infers the following arguments from their corresponding environment variables if they are not provided:
        - `api_key` from `QUARK_API_KEY`
        - `cookie` from `QUARK_COOKIE`
        """
        if api_key is None:
            api_key = os.environ.get("QUARK_API_KEY")
        if api_key is None:
            raise QuarkError(
                "The api_key client option must be set either by passing api_key to the client or by setting the QUARK_API_KEY environment variable"
            )
        self.api_key = api_key

        if cookie is None:
            cookie = os.environ.get("QUARK_COOKIE")
        self.cookie = cookie

        if base_url is None:
            base_url = os.environ.get("QUARK_BASE_URL")
        if base_url is None:
            base_url = f"https://demo.quarklabs.ai/api/v1"

        super().__init__(
            version=__version__,
            base_url=base_url,
            max_retries=max_retries,
            timeout=timeout,
            http_client=http_client,
            custom_headers=default_headers,
            custom_query=default_query,
            _strict_response_validation=_strict_response_validation,
        )

        self.context = context.ContextResource(self)
        self.admin = admin.AdminResource(self)
        self.models = models.ModelsResource(self)
        self.authorize = authorize.AuthorizeResource(self)
        self.profile = profile.ProfileResource(self)
        self.sources = sources.SourcesResource(self)
        self.users = users.UsersResource(self)
        self.json_schemas = json_schemas.JsonSchemasResource(self)
        self.history = history.HistoryResource(self)
        self.dataset = dataset.DatasetResource(self)
        self.worker = worker.WorkerResource(self)
        self.with_raw_response = QuarkWithRawResponse(self)
        self.with_streaming_response = QuarkWithStreamedResponse(self)

    @property
    @override
    def qs(self) -> Querystring:
        return Querystring(array_format="comma")

    @property
    @override
    def auth_headers(self) -> dict[str, str]:
        return {**self._bearer_auth, **self._cookie_auth}

    @property
    def _bearer_auth(self) -> dict[str, str]:
        api_key = self.api_key
        return {"Authorization": f"Bearer {api_key}"}

    @property
    def _cookie_auth(self) -> dict[str, str]:
        cookie = self.cookie
        if cookie is None:
            return {}
        return {"Cookie": cookie}

    @property
    @override
    def default_headers(self) -> dict[str, str | Omit]:
        return {
            **super().default_headers,
            "X-Stainless-Async": "false",
            **self._custom_headers,
        }

    def copy(
        self,
        *,
        api_key: str | None = None,
        cookie: str | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = NOT_GIVEN,
        http_client: httpx.Client | None = None,
        max_retries: int | NotGiven = NOT_GIVEN,
        default_headers: Mapping[str, str] | None = None,
        set_default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        set_default_query: Mapping[str, object] | None = None,
        _extra_kwargs: Mapping[str, Any] = {},
    ) -> Self:
        """
        Create a new client instance re-using the same options given to the current client with optional overriding.
        """
        if default_headers is not None and set_default_headers is not None:
            raise ValueError("The `default_headers` and `set_default_headers` arguments are mutually exclusive")

        if default_query is not None and set_default_query is not None:
            raise ValueError("The `default_query` and `set_default_query` arguments are mutually exclusive")

        headers = self._custom_headers
        if default_headers is not None:
            headers = {**headers, **default_headers}
        elif set_default_headers is not None:
            headers = set_default_headers

        params = self._custom_query
        if default_query is not None:
            params = {**params, **default_query}
        elif set_default_query is not None:
            params = set_default_query

        http_client = http_client or self._client
        return self.__class__(
            api_key=api_key or self.api_key,
            cookie=cookie or self.cookie,
            base_url=base_url or self.base_url,
            timeout=self.timeout if isinstance(timeout, NotGiven) else timeout,
            http_client=http_client,
            max_retries=max_retries if is_given(max_retries) else self.max_retries,
            default_headers=headers,
            default_query=params,
            **_extra_kwargs,
        )

    # Alias for `copy` for nicer inline usage, e.g.
    # client.with_options(timeout=10).foo.create(...)
    with_options = copy

    def retrieve(
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
        return self.get(
            "/",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    @override
    def _make_status_error(
        self,
        err_msg: str,
        *,
        body: object,
        response: httpx.Response,
    ) -> APIStatusError:
        if response.status_code == 400:
            return _exceptions.BadRequestError(err_msg, response=response, body=body)

        if response.status_code == 401:
            return _exceptions.AuthenticationError(err_msg, response=response, body=body)

        if response.status_code == 403:
            return _exceptions.PermissionDeniedError(err_msg, response=response, body=body)

        if response.status_code == 404:
            return _exceptions.NotFoundError(err_msg, response=response, body=body)

        if response.status_code == 409:
            return _exceptions.ConflictError(err_msg, response=response, body=body)

        if response.status_code == 422:
            return _exceptions.UnprocessableEntityError(err_msg, response=response, body=body)

        if response.status_code == 429:
            return _exceptions.RateLimitError(err_msg, response=response, body=body)

        if response.status_code >= 500:
            return _exceptions.InternalServerError(err_msg, response=response, body=body)
        return APIStatusError(err_msg, response=response, body=body)


class AsyncQuark(AsyncAPIClient):
    context: context.AsyncContextResource
    admin: admin.AsyncAdminResource
    models: models.AsyncModelsResource
    authorize: authorize.AsyncAuthorizeResource
    profile: profile.AsyncProfileResource
    sources: sources.AsyncSourcesResource
    users: users.AsyncUsersResource
    json_schemas: json_schemas.AsyncJsonSchemasResource
    history: history.AsyncHistoryResource
    dataset: dataset.AsyncDatasetResource
    worker: worker.AsyncWorkerResource
    with_raw_response: AsyncQuarkWithRawResponse
    with_streaming_response: AsyncQuarkWithStreamedResponse

    # client options
    api_key: str
    cookie: str | None

    def __init__(
        self,
        *,
        api_key: str | None = None,
        cookie: str | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: Union[float, Timeout, None, NotGiven] = NOT_GIVEN,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        # Configure a custom httpx client.
        # We provide a `DefaultAsyncHttpxClient` class that you can pass to retain the default values we use for `limits`, `timeout` & `follow_redirects`.
        # See the [httpx documentation](https://www.python-httpx.org/api/#asyncclient) for more details.
        http_client: httpx.AsyncClient | None = None,
        # Enable or disable schema validation for data returned by the API.
        # When enabled an error APIResponseValidationError is raised
        # if the API responds with invalid data for the expected schema.
        #
        # This parameter may be removed or changed in the future.
        # If you rely on this feature, please open a GitHub issue
        # outlining your use-case to help us decide if it should be
        # part of our public interface in the future.
        _strict_response_validation: bool = False,
    ) -> None:
        """Construct a new async AsyncQuark client instance.

        This automatically infers the following arguments from their corresponding environment variables if they are not provided:
        - `api_key` from `QUARK_API_KEY`
        - `cookie` from `QUARK_COOKIE`
        """
        if api_key is None:
            api_key = os.environ.get("QUARK_API_KEY")
        if api_key is None:
            raise QuarkError(
                "The api_key client option must be set either by passing api_key to the client or by setting the QUARK_API_KEY environment variable"
            )
        self.api_key = api_key

        if cookie is None:
            cookie = os.environ.get("QUARK_COOKIE")
        self.cookie = cookie

        if base_url is None:
            base_url = os.environ.get("QUARK_BASE_URL")
        if base_url is None:
            base_url = f"https://demo.quarklabs.ai/api/v1"

        super().__init__(
            version=__version__,
            base_url=base_url,
            max_retries=max_retries,
            timeout=timeout,
            http_client=http_client,
            custom_headers=default_headers,
            custom_query=default_query,
            _strict_response_validation=_strict_response_validation,
        )

        self.context = context.AsyncContextResource(self)
        self.admin = admin.AsyncAdminResource(self)
        self.models = models.AsyncModelsResource(self)
        self.authorize = authorize.AsyncAuthorizeResource(self)
        self.profile = profile.AsyncProfileResource(self)
        self.sources = sources.AsyncSourcesResource(self)
        self.users = users.AsyncUsersResource(self)
        self.json_schemas = json_schemas.AsyncJsonSchemasResource(self)
        self.history = history.AsyncHistoryResource(self)
        self.dataset = dataset.AsyncDatasetResource(self)
        self.worker = worker.AsyncWorkerResource(self)
        self.with_raw_response = AsyncQuarkWithRawResponse(self)
        self.with_streaming_response = AsyncQuarkWithStreamedResponse(self)

    @property
    @override
    def qs(self) -> Querystring:
        return Querystring(array_format="comma")

    @property
    @override
    def auth_headers(self) -> dict[str, str]:
        return {**self._bearer_auth, **self._cookie_auth}

    @property
    def _bearer_auth(self) -> dict[str, str]:
        api_key = self.api_key
        return {"Authorization": f"Bearer {api_key}"}

    @property
    def _cookie_auth(self) -> dict[str, str]:
        cookie = self.cookie
        if cookie is None:
            return {}
        return {"Cookie": cookie}

    @property
    @override
    def default_headers(self) -> dict[str, str | Omit]:
        return {
            **super().default_headers,
            "X-Stainless-Async": f"async:{get_async_library()}",
            **self._custom_headers,
        }

    def copy(
        self,
        *,
        api_key: str | None = None,
        cookie: str | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = NOT_GIVEN,
        http_client: httpx.AsyncClient | None = None,
        max_retries: int | NotGiven = NOT_GIVEN,
        default_headers: Mapping[str, str] | None = None,
        set_default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        set_default_query: Mapping[str, object] | None = None,
        _extra_kwargs: Mapping[str, Any] = {},
    ) -> Self:
        """
        Create a new client instance re-using the same options given to the current client with optional overriding.
        """
        if default_headers is not None and set_default_headers is not None:
            raise ValueError("The `default_headers` and `set_default_headers` arguments are mutually exclusive")

        if default_query is not None and set_default_query is not None:
            raise ValueError("The `default_query` and `set_default_query` arguments are mutually exclusive")

        headers = self._custom_headers
        if default_headers is not None:
            headers = {**headers, **default_headers}
        elif set_default_headers is not None:
            headers = set_default_headers

        params = self._custom_query
        if default_query is not None:
            params = {**params, **default_query}
        elif set_default_query is not None:
            params = set_default_query

        http_client = http_client or self._client
        return self.__class__(
            api_key=api_key or self.api_key,
            cookie=cookie or self.cookie,
            base_url=base_url or self.base_url,
            timeout=self.timeout if isinstance(timeout, NotGiven) else timeout,
            http_client=http_client,
            max_retries=max_retries if is_given(max_retries) else self.max_retries,
            default_headers=headers,
            default_query=params,
            **_extra_kwargs,
        )

    # Alias for `copy` for nicer inline usage, e.g.
    # client.with_options(timeout=10).foo.create(...)
    with_options = copy

    async def retrieve(
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
        return await self.get(
            "/",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    @override
    def _make_status_error(
        self,
        err_msg: str,
        *,
        body: object,
        response: httpx.Response,
    ) -> APIStatusError:
        if response.status_code == 400:
            return _exceptions.BadRequestError(err_msg, response=response, body=body)

        if response.status_code == 401:
            return _exceptions.AuthenticationError(err_msg, response=response, body=body)

        if response.status_code == 403:
            return _exceptions.PermissionDeniedError(err_msg, response=response, body=body)

        if response.status_code == 404:
            return _exceptions.NotFoundError(err_msg, response=response, body=body)

        if response.status_code == 409:
            return _exceptions.ConflictError(err_msg, response=response, body=body)

        if response.status_code == 422:
            return _exceptions.UnprocessableEntityError(err_msg, response=response, body=body)

        if response.status_code == 429:
            return _exceptions.RateLimitError(err_msg, response=response, body=body)

        if response.status_code >= 500:
            return _exceptions.InternalServerError(err_msg, response=response, body=body)
        return APIStatusError(err_msg, response=response, body=body)


class QuarkWithRawResponse:
    def __init__(self, client: Quark) -> None:
        self.context = context.ContextResourceWithRawResponse(client.context)
        self.admin = admin.AdminResourceWithRawResponse(client.admin)
        self.models = models.ModelsResourceWithRawResponse(client.models)
        self.authorize = authorize.AuthorizeResourceWithRawResponse(client.authorize)
        self.profile = profile.ProfileResourceWithRawResponse(client.profile)
        self.sources = sources.SourcesResourceWithRawResponse(client.sources)
        self.users = users.UsersResourceWithRawResponse(client.users)
        self.json_schemas = json_schemas.JsonSchemasResourceWithRawResponse(client.json_schemas)
        self.history = history.HistoryResourceWithRawResponse(client.history)
        self.dataset = dataset.DatasetResourceWithRawResponse(client.dataset)
        self.worker = worker.WorkerResourceWithRawResponse(client.worker)

        self.retrieve = to_raw_response_wrapper(
            client.retrieve,
        )


class AsyncQuarkWithRawResponse:
    def __init__(self, client: AsyncQuark) -> None:
        self.context = context.AsyncContextResourceWithRawResponse(client.context)
        self.admin = admin.AsyncAdminResourceWithRawResponse(client.admin)
        self.models = models.AsyncModelsResourceWithRawResponse(client.models)
        self.authorize = authorize.AsyncAuthorizeResourceWithRawResponse(client.authorize)
        self.profile = profile.AsyncProfileResourceWithRawResponse(client.profile)
        self.sources = sources.AsyncSourcesResourceWithRawResponse(client.sources)
        self.users = users.AsyncUsersResourceWithRawResponse(client.users)
        self.json_schemas = json_schemas.AsyncJsonSchemasResourceWithRawResponse(client.json_schemas)
        self.history = history.AsyncHistoryResourceWithRawResponse(client.history)
        self.dataset = dataset.AsyncDatasetResourceWithRawResponse(client.dataset)
        self.worker = worker.AsyncWorkerResourceWithRawResponse(client.worker)

        self.retrieve = async_to_raw_response_wrapper(
            client.retrieve,
        )


class QuarkWithStreamedResponse:
    def __init__(self, client: Quark) -> None:
        self.context = context.ContextResourceWithStreamingResponse(client.context)
        self.admin = admin.AdminResourceWithStreamingResponse(client.admin)
        self.models = models.ModelsResourceWithStreamingResponse(client.models)
        self.authorize = authorize.AuthorizeResourceWithStreamingResponse(client.authorize)
        self.profile = profile.ProfileResourceWithStreamingResponse(client.profile)
        self.sources = sources.SourcesResourceWithStreamingResponse(client.sources)
        self.users = users.UsersResourceWithStreamingResponse(client.users)
        self.json_schemas = json_schemas.JsonSchemasResourceWithStreamingResponse(client.json_schemas)
        self.history = history.HistoryResourceWithStreamingResponse(client.history)
        self.dataset = dataset.DatasetResourceWithStreamingResponse(client.dataset)
        self.worker = worker.WorkerResourceWithStreamingResponse(client.worker)

        self.retrieve = to_streamed_response_wrapper(
            client.retrieve,
        )


class AsyncQuarkWithStreamedResponse:
    def __init__(self, client: AsyncQuark) -> None:
        self.context = context.AsyncContextResourceWithStreamingResponse(client.context)
        self.admin = admin.AsyncAdminResourceWithStreamingResponse(client.admin)
        self.models = models.AsyncModelsResourceWithStreamingResponse(client.models)
        self.authorize = authorize.AsyncAuthorizeResourceWithStreamingResponse(client.authorize)
        self.profile = profile.AsyncProfileResourceWithStreamingResponse(client.profile)
        self.sources = sources.AsyncSourcesResourceWithStreamingResponse(client.sources)
        self.users = users.AsyncUsersResourceWithStreamingResponse(client.users)
        self.json_schemas = json_schemas.AsyncJsonSchemasResourceWithStreamingResponse(client.json_schemas)
        self.history = history.AsyncHistoryResourceWithStreamingResponse(client.history)
        self.dataset = dataset.AsyncDatasetResourceWithStreamingResponse(client.dataset)
        self.worker = worker.AsyncWorkerResourceWithStreamingResponse(client.worker)

        self.retrieve = async_to_streamed_response_wrapper(
            client.retrieve,
        )


Client = Quark

AsyncClient = AsyncQuark
