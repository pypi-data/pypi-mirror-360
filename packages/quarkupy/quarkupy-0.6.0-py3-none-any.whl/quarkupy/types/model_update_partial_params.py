# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from datetime import datetime
from typing_extensions import Literal, Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["ModelUpdatePartialParams"]


class ModelUpdatePartialParams(TypedDict, total=False):
    config: Required[object]
    """# Provider-specific configuration (JSON)"""

    model_provider: Required[Literal["Native", "Onnx", "OpenAI", "Other"]]
    """# Model Provider"""

    model_type: Required[Literal["Local", "API", "Other"]]
    """# Model Type"""

    name: Required[str]
    """# Model Name"""

    owned_by_identity_id: Required[str]
    """# Model Owner"""

    description: str
    """# Description"""

    updated_at: Annotated[Union[str, datetime], PropertyInfo(format="iso8601")]
