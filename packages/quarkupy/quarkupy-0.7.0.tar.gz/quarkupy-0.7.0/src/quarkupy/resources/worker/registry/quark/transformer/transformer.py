# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from ......_compat import cached_property
from ......_resource import SyncAPIResource, AsyncAPIResource
from .docling_chunker import (
    DoclingChunkerResource,
    AsyncDoclingChunkerResource,
    DoclingChunkerResourceWithRawResponse,
    AsyncDoclingChunkerResourceWithRawResponse,
    DoclingChunkerResourceWithStreamingResponse,
    AsyncDoclingChunkerResourceWithStreamingResponse,
)
from .handlebars_base import (
    HandlebarsBaseResource,
    AsyncHandlebarsBaseResource,
    HandlebarsBaseResourceWithRawResponse,
    AsyncHandlebarsBaseResourceWithRawResponse,
    HandlebarsBaseResourceWithStreamingResponse,
    AsyncHandlebarsBaseResourceWithStreamingResponse,
)
from .parse_extractor_llm import (
    ParseExtractorLlmResource,
    AsyncParseExtractorLlmResource,
    ParseExtractorLlmResourceWithRawResponse,
    AsyncParseExtractorLlmResourceWithRawResponse,
    ParseExtractorLlmResourceWithStreamingResponse,
    AsyncParseExtractorLlmResourceWithStreamingResponse,
)
from .parse_classifier_llm import (
    ParseClassifierLlmResource,
    AsyncParseClassifierLlmResource,
    ParseClassifierLlmResourceWithRawResponse,
    AsyncParseClassifierLlmResourceWithRawResponse,
    ParseClassifierLlmResourceWithStreamingResponse,
    AsyncParseClassifierLlmResourceWithStreamingResponse,
)
from .onnx_sat_segmentation import (
    OnnxSatSegmentationResource,
    AsyncOnnxSatSegmentationResource,
    OnnxSatSegmentationResourceWithRawResponse,
    AsyncOnnxSatSegmentationResourceWithRawResponse,
    OnnxSatSegmentationResourceWithStreamingResponse,
    AsyncOnnxSatSegmentationResourceWithStreamingResponse,
)
from .context_extract_prompt import (
    ContextExtractPromptResource,
    AsyncContextExtractPromptResource,
    ContextExtractPromptResourceWithRawResponse,
    AsyncContextExtractPromptResourceWithRawResponse,
    ContextExtractPromptResourceWithStreamingResponse,
    AsyncContextExtractPromptResourceWithStreamingResponse,
)
from .context_classifier_prompt import (
    ContextClassifierPromptResource,
    AsyncContextClassifierPromptResource,
    ContextClassifierPromptResourceWithRawResponse,
    AsyncContextClassifierPromptResourceWithRawResponse,
    ContextClassifierPromptResourceWithStreamingResponse,
    AsyncContextClassifierPromptResourceWithStreamingResponse,
)

__all__ = ["TransformerResource", "AsyncTransformerResource"]


class TransformerResource(SyncAPIResource):
    @cached_property
    def docling_chunker(self) -> DoclingChunkerResource:
        return DoclingChunkerResource(self._client)

    @cached_property
    def handlebars_base(self) -> HandlebarsBaseResource:
        return HandlebarsBaseResource(self._client)

    @cached_property
    def onnx_sat_segmentation(self) -> OnnxSatSegmentationResource:
        return OnnxSatSegmentationResource(self._client)

    @cached_property
    def context_extract_prompt(self) -> ContextExtractPromptResource:
        return ContextExtractPromptResource(self._client)

    @cached_property
    def parse_extractor_llm(self) -> ParseExtractorLlmResource:
        return ParseExtractorLlmResource(self._client)

    @cached_property
    def context_classifier_prompt(self) -> ContextClassifierPromptResource:
        return ContextClassifierPromptResource(self._client)

    @cached_property
    def parse_classifier_llm(self) -> ParseClassifierLlmResource:
        return ParseClassifierLlmResource(self._client)

    @cached_property
    def with_raw_response(self) -> TransformerResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/quarklabsai/quarkupy#accessing-raw-response-data-eg-headers
        """
        return TransformerResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> TransformerResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/quarklabsai/quarkupy#with_streaming_response
        """
        return TransformerResourceWithStreamingResponse(self)


class AsyncTransformerResource(AsyncAPIResource):
    @cached_property
    def docling_chunker(self) -> AsyncDoclingChunkerResource:
        return AsyncDoclingChunkerResource(self._client)

    @cached_property
    def handlebars_base(self) -> AsyncHandlebarsBaseResource:
        return AsyncHandlebarsBaseResource(self._client)

    @cached_property
    def onnx_sat_segmentation(self) -> AsyncOnnxSatSegmentationResource:
        return AsyncOnnxSatSegmentationResource(self._client)

    @cached_property
    def context_extract_prompt(self) -> AsyncContextExtractPromptResource:
        return AsyncContextExtractPromptResource(self._client)

    @cached_property
    def parse_extractor_llm(self) -> AsyncParseExtractorLlmResource:
        return AsyncParseExtractorLlmResource(self._client)

    @cached_property
    def context_classifier_prompt(self) -> AsyncContextClassifierPromptResource:
        return AsyncContextClassifierPromptResource(self._client)

    @cached_property
    def parse_classifier_llm(self) -> AsyncParseClassifierLlmResource:
        return AsyncParseClassifierLlmResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncTransformerResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/quarklabsai/quarkupy#accessing-raw-response-data-eg-headers
        """
        return AsyncTransformerResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncTransformerResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/quarklabsai/quarkupy#with_streaming_response
        """
        return AsyncTransformerResourceWithStreamingResponse(self)


class TransformerResourceWithRawResponse:
    def __init__(self, transformer: TransformerResource) -> None:
        self._transformer = transformer

    @cached_property
    def docling_chunker(self) -> DoclingChunkerResourceWithRawResponse:
        return DoclingChunkerResourceWithRawResponse(self._transformer.docling_chunker)

    @cached_property
    def handlebars_base(self) -> HandlebarsBaseResourceWithRawResponse:
        return HandlebarsBaseResourceWithRawResponse(self._transformer.handlebars_base)

    @cached_property
    def onnx_sat_segmentation(self) -> OnnxSatSegmentationResourceWithRawResponse:
        return OnnxSatSegmentationResourceWithRawResponse(self._transformer.onnx_sat_segmentation)

    @cached_property
    def context_extract_prompt(self) -> ContextExtractPromptResourceWithRawResponse:
        return ContextExtractPromptResourceWithRawResponse(self._transformer.context_extract_prompt)

    @cached_property
    def parse_extractor_llm(self) -> ParseExtractorLlmResourceWithRawResponse:
        return ParseExtractorLlmResourceWithRawResponse(self._transformer.parse_extractor_llm)

    @cached_property
    def context_classifier_prompt(self) -> ContextClassifierPromptResourceWithRawResponse:
        return ContextClassifierPromptResourceWithRawResponse(self._transformer.context_classifier_prompt)

    @cached_property
    def parse_classifier_llm(self) -> ParseClassifierLlmResourceWithRawResponse:
        return ParseClassifierLlmResourceWithRawResponse(self._transformer.parse_classifier_llm)


class AsyncTransformerResourceWithRawResponse:
    def __init__(self, transformer: AsyncTransformerResource) -> None:
        self._transformer = transformer

    @cached_property
    def docling_chunker(self) -> AsyncDoclingChunkerResourceWithRawResponse:
        return AsyncDoclingChunkerResourceWithRawResponse(self._transformer.docling_chunker)

    @cached_property
    def handlebars_base(self) -> AsyncHandlebarsBaseResourceWithRawResponse:
        return AsyncHandlebarsBaseResourceWithRawResponse(self._transformer.handlebars_base)

    @cached_property
    def onnx_sat_segmentation(self) -> AsyncOnnxSatSegmentationResourceWithRawResponse:
        return AsyncOnnxSatSegmentationResourceWithRawResponse(self._transformer.onnx_sat_segmentation)

    @cached_property
    def context_extract_prompt(self) -> AsyncContextExtractPromptResourceWithRawResponse:
        return AsyncContextExtractPromptResourceWithRawResponse(self._transformer.context_extract_prompt)

    @cached_property
    def parse_extractor_llm(self) -> AsyncParseExtractorLlmResourceWithRawResponse:
        return AsyncParseExtractorLlmResourceWithRawResponse(self._transformer.parse_extractor_llm)

    @cached_property
    def context_classifier_prompt(self) -> AsyncContextClassifierPromptResourceWithRawResponse:
        return AsyncContextClassifierPromptResourceWithRawResponse(self._transformer.context_classifier_prompt)

    @cached_property
    def parse_classifier_llm(self) -> AsyncParseClassifierLlmResourceWithRawResponse:
        return AsyncParseClassifierLlmResourceWithRawResponse(self._transformer.parse_classifier_llm)


class TransformerResourceWithStreamingResponse:
    def __init__(self, transformer: TransformerResource) -> None:
        self._transformer = transformer

    @cached_property
    def docling_chunker(self) -> DoclingChunkerResourceWithStreamingResponse:
        return DoclingChunkerResourceWithStreamingResponse(self._transformer.docling_chunker)

    @cached_property
    def handlebars_base(self) -> HandlebarsBaseResourceWithStreamingResponse:
        return HandlebarsBaseResourceWithStreamingResponse(self._transformer.handlebars_base)

    @cached_property
    def onnx_sat_segmentation(self) -> OnnxSatSegmentationResourceWithStreamingResponse:
        return OnnxSatSegmentationResourceWithStreamingResponse(self._transformer.onnx_sat_segmentation)

    @cached_property
    def context_extract_prompt(self) -> ContextExtractPromptResourceWithStreamingResponse:
        return ContextExtractPromptResourceWithStreamingResponse(self._transformer.context_extract_prompt)

    @cached_property
    def parse_extractor_llm(self) -> ParseExtractorLlmResourceWithStreamingResponse:
        return ParseExtractorLlmResourceWithStreamingResponse(self._transformer.parse_extractor_llm)

    @cached_property
    def context_classifier_prompt(self) -> ContextClassifierPromptResourceWithStreamingResponse:
        return ContextClassifierPromptResourceWithStreamingResponse(self._transformer.context_classifier_prompt)

    @cached_property
    def parse_classifier_llm(self) -> ParseClassifierLlmResourceWithStreamingResponse:
        return ParseClassifierLlmResourceWithStreamingResponse(self._transformer.parse_classifier_llm)


class AsyncTransformerResourceWithStreamingResponse:
    def __init__(self, transformer: AsyncTransformerResource) -> None:
        self._transformer = transformer

    @cached_property
    def docling_chunker(self) -> AsyncDoclingChunkerResourceWithStreamingResponse:
        return AsyncDoclingChunkerResourceWithStreamingResponse(self._transformer.docling_chunker)

    @cached_property
    def handlebars_base(self) -> AsyncHandlebarsBaseResourceWithStreamingResponse:
        return AsyncHandlebarsBaseResourceWithStreamingResponse(self._transformer.handlebars_base)

    @cached_property
    def onnx_sat_segmentation(self) -> AsyncOnnxSatSegmentationResourceWithStreamingResponse:
        return AsyncOnnxSatSegmentationResourceWithStreamingResponse(self._transformer.onnx_sat_segmentation)

    @cached_property
    def context_extract_prompt(self) -> AsyncContextExtractPromptResourceWithStreamingResponse:
        return AsyncContextExtractPromptResourceWithStreamingResponse(self._transformer.context_extract_prompt)

    @cached_property
    def parse_extractor_llm(self) -> AsyncParseExtractorLlmResourceWithStreamingResponse:
        return AsyncParseExtractorLlmResourceWithStreamingResponse(self._transformer.parse_extractor_llm)

    @cached_property
    def context_classifier_prompt(self) -> AsyncContextClassifierPromptResourceWithStreamingResponse:
        return AsyncContextClassifierPromptResourceWithStreamingResponse(self._transformer.context_classifier_prompt)

    @cached_property
    def parse_classifier_llm(self) -> AsyncParseClassifierLlmResourceWithStreamingResponse:
        return AsyncParseClassifierLlmResourceWithStreamingResponse(self._transformer.parse_classifier_llm)
