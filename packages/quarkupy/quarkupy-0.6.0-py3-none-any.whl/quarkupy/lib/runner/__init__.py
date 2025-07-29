from __future__ import annotations, absolute_import

from quarkupy.types.history import FlowHistoryItem, QuarkHistoryItem
from quarkupy.types.worker.registry import QuarkRegistryItem


from .driver import *
from .inputs import *
from .quarks import *

LatticeStatus = Literal["New", "Scheduled", "Running", "Completed", "Failed"]
QuarkStatus = Literal["New", "Scheduled", "Running", "OutputStaged", "Completed", "Failed"]

__all__ = [
    "QuarkRemoteDriver",
    "LatticeStatus",
    "QuarkStatus",
    "QuarkInput",
    "QuarkHistoryItem",
    "QuarkRegistryItem",
    "FlowHistoryItem",
    "ContextClassifierPromptInput",
    "ContextExtractPromptInput",
    "ParseClassifierLlmInput",
    "ParseExtractorLlmInput",
    "S3ReadCSVQuarkInput",
    "S3ReadWholeFileQuarkInput",
    "DocExtractQuarkInput",
    "TextTemplateInput",
    "OpenAIEmbeddingsInput",
    "OpenAICompletionsInput",
    "DocChunkerQuarkInput",
    "SnowflakeReadInput",
    "VectorDBIngestInput",
    "VectorDBSearchInput",
    "OpenAICompletionBaseQuark",
    "OpenAIEmbeddingsQuark",
    "OpendalInput",
    "ConfigOpendalConfigInputOpendalS3Config",
    "ConfigOpendalConfigInputOpendalMemoryConfig",
    "ConfigOpendalConfigInputOpendalGDriveConfig",
    "ConfigOpendalConfigInputOpendalOneDriveConfig",
    "OpendalReadQuark",
    "DocExtractQuark",
    "DocChunkerQuark",
    "VectorDBIngestQuark",
    "VectorDBSearchQuark",
    "S3ReadCSVQuark",
    "S3ReadWholeFileQuark",
    "TextTemplateBaseQuark",
    "DocChunkerQuark",
]
