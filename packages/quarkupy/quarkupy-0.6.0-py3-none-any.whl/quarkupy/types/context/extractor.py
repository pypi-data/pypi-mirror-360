# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from ..._models import BaseModel
from .reference_depth import ReferenceDepth

__all__ = ["Extractor"]


class Extractor(BaseModel):
    data_type: Literal["String", "Boolean", "Integer", "Float", "Rating", "Object", "Date", "Label"]
    """# Type of data to extract"""

    api_model_role_id: str = FieldInfo(alias="model_role_id")
    """# Model Role to use for extraction"""

    name: str
    """# Extractor Name"""

    owned_by_identity_id: str
    """# Owner"""

    reference_depth: ReferenceDepth
    """# Match Segments or Sentences"""

    add_reason: Optional[bool] = None
    """# Add reason for extracting this data"""

    add_references: Optional[bool] = None
    """# Add references to the extracted data

    Default is true
    """

    config: Optional[object] = None

    created_at: Optional[datetime] = None
    """# Created"""

    description: Optional[str] = None
    """# Extractor Description

    Note: the LLM uses this to perform the extraction, so be descriptive
    """

    examples: Optional[object] = None
    """# Examples of the data to extract"""

    extractor_id: Optional[str] = None
    """# Extractor ID"""

    updated_at: Optional[datetime] = None
    """# Updated"""
