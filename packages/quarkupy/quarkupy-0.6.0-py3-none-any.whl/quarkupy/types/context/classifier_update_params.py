# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from datetime import datetime
from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo
from .reference_depth import ReferenceDepth

__all__ = ["ClassifierUpdateParams"]


class ClassifierUpdateParams(TypedDict, total=False):
    model_role_id: Required[str]
    """# Model Role

    Determines which model executes the classifier
    """

    name: Required[str]
    """# Classifier Name"""

    owned_by_identity_id: Required[str]
    """# Owner ID"""

    reference_depth: Required[ReferenceDepth]
    """# Match Segments or Sentences?"""

    description: str
    """# Classifier Description

    Note: the LLM uses this for matching so be descriptive
    """

    parent_classifier_id: str

    updated_at: Annotated[Union[str, datetime], PropertyInfo(format="iso8601")]
    """# Last Updated"""
