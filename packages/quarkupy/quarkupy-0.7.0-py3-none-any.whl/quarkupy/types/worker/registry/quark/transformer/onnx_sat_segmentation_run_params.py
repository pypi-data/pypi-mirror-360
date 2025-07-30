# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["OnnxSatSegmentationRunParams"]


class OnnxSatSegmentationRunParams(TypedDict, total=False):
    flow_id: Required[str]

    ipc_dataset_id: Required[str]

    opt_input_column: str

    opt_paragraph_threshold: float
    """Threshold for paragraph boundary detection (default: 0.5)"""

    opt_segmentation_mode: Literal["SentencesOnly", "ParagraphsOnly", "SentencesAndParagraphs"]
    """Segmentation mode: SentencesOnly, ParagraphsOnly, or SentencesAndParagraphs"""

    opt_sentence_threshold: float
    """Threshold for sentence boundary detection (default: 0.25)"""
