# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from ......_compat import cached_property
from ......_resource import SyncAPIResource, AsyncAPIResource
from .openai_embeddings import (
    OpenAIEmbeddingsResource,
    AsyncOpenAIEmbeddingsResource,
    OpenAIEmbeddingsResourceWithRawResponse,
    AsyncOpenAIEmbeddingsResourceWithRawResponse,
    OpenAIEmbeddingsResourceWithStreamingResponse,
    AsyncOpenAIEmbeddingsResourceWithStreamingResponse,
)
from .openai_completion_base import (
    OpenAICompletionBaseResource,
    AsyncOpenAICompletionBaseResource,
    OpenAICompletionBaseResourceWithRawResponse,
    AsyncOpenAICompletionBaseResourceWithRawResponse,
    OpenAICompletionBaseResourceWithStreamingResponse,
    AsyncOpenAICompletionBaseResourceWithStreamingResponse,
)

__all__ = ["AIResource", "AsyncAIResource"]


class AIResource(SyncAPIResource):
    @cached_property
    def openai_embeddings(self) -> OpenAIEmbeddingsResource:
        return OpenAIEmbeddingsResource(self._client)

    @cached_property
    def openai_completion_base(self) -> OpenAICompletionBaseResource:
        return OpenAICompletionBaseResource(self._client)

    @cached_property
    def with_raw_response(self) -> AIResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/quarklabsai/quarkupy#accessing-raw-response-data-eg-headers
        """
        return AIResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AIResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/quarklabsai/quarkupy#with_streaming_response
        """
        return AIResourceWithStreamingResponse(self)


class AsyncAIResource(AsyncAPIResource):
    @cached_property
    def openai_embeddings(self) -> AsyncOpenAIEmbeddingsResource:
        return AsyncOpenAIEmbeddingsResource(self._client)

    @cached_property
    def openai_completion_base(self) -> AsyncOpenAICompletionBaseResource:
        return AsyncOpenAICompletionBaseResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncAIResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/quarklabsai/quarkupy#accessing-raw-response-data-eg-headers
        """
        return AsyncAIResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncAIResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/quarklabsai/quarkupy#with_streaming_response
        """
        return AsyncAIResourceWithStreamingResponse(self)


class AIResourceWithRawResponse:
    def __init__(self, ai: AIResource) -> None:
        self._ai = ai

    @cached_property
    def openai_embeddings(self) -> OpenAIEmbeddingsResourceWithRawResponse:
        return OpenAIEmbeddingsResourceWithRawResponse(self._ai.openai_embeddings)

    @cached_property
    def openai_completion_base(self) -> OpenAICompletionBaseResourceWithRawResponse:
        return OpenAICompletionBaseResourceWithRawResponse(self._ai.openai_completion_base)


class AsyncAIResourceWithRawResponse:
    def __init__(self, ai: AsyncAIResource) -> None:
        self._ai = ai

    @cached_property
    def openai_embeddings(self) -> AsyncOpenAIEmbeddingsResourceWithRawResponse:
        return AsyncOpenAIEmbeddingsResourceWithRawResponse(self._ai.openai_embeddings)

    @cached_property
    def openai_completion_base(self) -> AsyncOpenAICompletionBaseResourceWithRawResponse:
        return AsyncOpenAICompletionBaseResourceWithRawResponse(self._ai.openai_completion_base)


class AIResourceWithStreamingResponse:
    def __init__(self, ai: AIResource) -> None:
        self._ai = ai

    @cached_property
    def openai_embeddings(self) -> OpenAIEmbeddingsResourceWithStreamingResponse:
        return OpenAIEmbeddingsResourceWithStreamingResponse(self._ai.openai_embeddings)

    @cached_property
    def openai_completion_base(self) -> OpenAICompletionBaseResourceWithStreamingResponse:
        return OpenAICompletionBaseResourceWithStreamingResponse(self._ai.openai_completion_base)


class AsyncAIResourceWithStreamingResponse:
    def __init__(self, ai: AsyncAIResource) -> None:
        self._ai = ai

    @cached_property
    def openai_embeddings(self) -> AsyncOpenAIEmbeddingsResourceWithStreamingResponse:
        return AsyncOpenAIEmbeddingsResourceWithStreamingResponse(self._ai.openai_embeddings)

    @cached_property
    def openai_completion_base(self) -> AsyncOpenAICompletionBaseResourceWithStreamingResponse:
        return AsyncOpenAICompletionBaseResourceWithStreamingResponse(self._ai.openai_completion_base)
