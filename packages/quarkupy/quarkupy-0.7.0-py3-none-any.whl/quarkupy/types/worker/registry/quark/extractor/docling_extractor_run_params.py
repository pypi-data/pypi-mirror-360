# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Literal, Required, TypedDict

__all__ = ["DoclingExtractorRunParams"]


class DoclingExtractorRunParams(TypedDict, total=False):
    ipc_dataset_id: Required[str]

    lattice_id: Required[str]

    opt_device: str
    """Device to use for acceleration - options are CPU, CUDA, MPS, or AUTO

    Default is AUTO
    """

    opt_do_cell_matching: bool
    """Default is [false]"""

    opt_do_ocr: bool
    """Whether to perform OCR

    Default is [true]
    """

    opt_do_table_structure: bool
    """Default is [false]"""

    opt_generate_page_images: bool
    """Default: [true]"""

    opt_generate_picture_images: bool
    """Default: [true]"""

    opt_image_resolution_scale: float
    """Default: 2.0"""

    opt_input_file_types: List[Literal["AsciiDoc", "Docx", "HTML", "Image", "Markdown", "PDF", "PPTX"]]
    """Limit input types

    Default is [Nome] - all supported
    """

    opt_max_file_size: int
    """Limit the size of the file to extract from (in bytes)

    Default: [None]
    """

    opt_max_pages: int
    """Limit the number of pages to extract

    Default is [None]
    """

    opt_output_type: Literal["DocTags", "HTML", "JSON", "Markdown", "Text"]
    """Supported output types for Docling"""

    opt_use_gpu: bool
    """Best effort to use GPU

    Default is [true]
    """
