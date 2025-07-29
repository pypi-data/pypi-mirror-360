# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["MlModel"]


class MlModel(BaseModel):
    config: object
    """# Provider-specific configuration (JSON)"""

    api_model_provider: Literal["Native", "Onnx", "OpenAI", "Other"] = FieldInfo(alias="model_provider")
    """# Model Provider"""

    api_model_type: Literal["Local", "API", "Other"] = FieldInfo(alias="model_type")
    """# Model Type"""

    name: str
    """# Model Name"""

    owned_by_identity_id: str
    """# Model Owner"""

    created_at: Optional[datetime] = None

    description: Optional[str] = None
    """# Description"""

    api_model_id: Optional[str] = FieldInfo(alias="model_id", default=None)
    """# Model ID"""

    updated_at: Optional[datetime] = None
