# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from datetime import datetime
from typing_extensions import Literal, Required, Annotated, TypedDict

from ..._utils import PropertyInfo
from .reference_depth import ReferenceDepth

__all__ = ["ExtractorUpdateParams"]


class ExtractorUpdateParams(TypedDict, total=False):
    data_type: Required[Literal["String", "Boolean", "Integer", "Float", "Rating", "Object", "Date", "Label"]]
    """# Type of data to extract"""

    model_role_id: Required[str]
    """# Model Role to use for extraction"""

    name: Required[str]
    """# Extractor Name"""

    owned_by_identity_id: Required[str]
    """# Owner"""

    reference_depth: Required[ReferenceDepth]
    """# Match Segments or Sentences"""

    add_reason: bool
    """# Add reason for extracting this data"""

    add_references: bool
    """# Add references to the extracted data

    Default is true
    """

    config: object

    description: str
    """# Extractor Description

    Note: the LLM uses this to perform the extraction, so be descriptive
    """

    examples: object
    """# Examples of the data to extract"""

    updated_at: Annotated[Union[str, datetime], PropertyInfo(format="iso8601")]
    """# Updated"""
