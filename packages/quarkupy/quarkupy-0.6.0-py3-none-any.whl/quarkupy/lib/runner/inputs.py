from typing import Union

from quarkupy.types.worker.registry.quark.ai import (
    OpenAIEmbeddingRunParams as OpenAIEmbeddingsInput,
    OpenAICompletionBaseRunParams as OpenAICompletionsInput,
)
from quarkupy.types.worker.registry.quark.files import (
    OpendalRunParams as OpendalInput,
    S3ReadFilesBinaryRunParams as S3ReadCSVQuarkInput,
    S3ReadFilesBinaryRunParams as S3ReadWholeFileQuarkInput,
)
from quarkupy.types.worker.registry.quark.files.opendal_run_params import (
    ConfigOpendalConfigInputOpendalS3Config,
    ConfigOpendalConfigInputOpendalMemoryConfig,
    ConfigOpendalConfigInputOpendalGDriveConfig,
    ConfigOpendalConfigInputOpendalOneDriveConfig,
)
from quarkupy.types.worker.registry.quark.vector import (
    LancedbIngestRunParams as VectorDBIngestInput,
    LancedbSearchRunParams as VectorDBSearchInput,
)
from quarkupy.types.worker.registry.quark.other import (
    ContextInsertObjectRunParams as ContextInsertObjectsInput,
    ContextInsertSegmentRunParams as ContextInsertSegmentsInput,
    ContextInsertClassifiedSegmentRunParams as ContextInsertClassifiedSegmentsInput,
    ContextInsertExtractedSegmentRunParams as ContextInsertExtractedSegmentsInput
)
from quarkupy.types.worker.registry.quark.databases import SnowflakeReadRunParams as SnowflakeReadInput
from quarkupy.types.worker.registry.quark.extractor import DoclingExtractorRunParams as DocExtractQuarkInput
from quarkupy.types.worker.registry.quark.transformer import (
    DoclingChunkerRunParams as DocChunkerQuarkInput,
    HandlebarsBaseRunParams as TextTemplateInput,
    ParseExtractorLlmRunParams as ParseExtractorLlmInput,
    ParseClassifierLlmRunParams as ParseClassifierLlmInput,
    OnnxSatSegmentationRunParams as SaTSegmentationInput,
    ContextExtractPromptRunParams as ContextExtractPromptInput,
    ContextClassifierPromptRunParams as ContextClassifierPromptInput,
)

QuarkInput = Union[
    ContextClassifierPromptInput,
    ContextExtractPromptInput,
    ContextInsertObjectsInput,
    ContextInsertSegmentsInput,
    ContextInsertClassifiedSegmentsInput,
    ContextInsertExtractedSegmentsInput,
    ConfigOpendalConfigInputOpendalS3Config,
    ConfigOpendalConfigInputOpendalMemoryConfig,
    ConfigOpendalConfigInputOpendalGDriveConfig,
    ConfigOpendalConfigInputOpendalOneDriveConfig,
    DocChunkerQuarkInput,
    DocExtractQuarkInput,
    OpenAIEmbeddingsInput,
    OpenAICompletionsInput,
    OpendalInput,
    ParseClassifierLlmInput,
    ParseExtractorLlmInput,
    S3ReadCSVQuarkInput,
    S3ReadWholeFileQuarkInput,
    SaTSegmentationInput,
    SnowflakeReadInput,
    TextTemplateInput,
    VectorDBIngestInput,
    VectorDBSearchInput,
    None,
]

__all__ = [
    "QuarkInput",
    "ContextClassifierPromptInput",
    "ContextExtractPromptInput",
    "ContextInsertObjectsInput",
    "ContextInsertSegmentsInput",
    "ContextInsertClassifiedSegmentsInput",
    "ContextInsertExtractedSegmentsInput",
    "ConfigOpendalConfigInputOpendalS3Config",
    "ConfigOpendalConfigInputOpendalMemoryConfig",
    "ConfigOpendalConfigInputOpendalGDriveConfig",
    "ConfigOpendalConfigInputOpendalOneDriveConfig",
    "DocChunkerQuarkInput",
    "DocExtractQuarkInput",
    "OpenAIEmbeddingsInput",
    "OpenAICompletionsInput",
    "OpendalInput",
    "ParseClassifierLlmInput",
    "ParseExtractorLlmInput",
    "S3ReadCSVQuarkInput",
    "S3ReadWholeFileQuarkInput",
    "SaTSegmentationInput",
    "SnowflakeReadInput",
    "TextTemplateInput",
    "VectorDBIngestInput",
    "VectorDBSearchInput",
]
