# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime

from pydantic import Field as FieldInfo

from ..._models import BaseModel
from .reference_depth import ReferenceDepth

__all__ = ["Classifier"]


class Classifier(BaseModel):
    api_model_role_id: str = FieldInfo(alias="model_role_id")
    """# Model Role

    Determines which model executes the classifier
    """

    name: str
    """# Classifier Name"""

    owned_by_identity_id: str
    """# Owner ID"""

    reference_depth: ReferenceDepth
    """# Match Segments or Sentences?"""

    classifier_id: Optional[str] = None
    """# Classifier ID"""

    created_at: Optional[datetime] = None
    """# Created"""

    description: Optional[str] = None
    """# Classifier Description

    Note: the LLM uses this for matching so be descriptive
    """

    parent_classifier_id: Optional[str] = None

    updated_at: Optional[datetime] = None
    """# Last Updated"""
