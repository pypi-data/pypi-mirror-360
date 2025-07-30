# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["MlModelRole"]


class MlModelRole(BaseModel):
    config_override: object
    """# Optional Override for Model Configuration"""

    api_model_id: str = FieldInfo(alias="model_id")
    """# Associated Model"""

    name: str
    """# Model Role Name"""

    owned_by_identity_id: str
    """# Model Role Owner"""

    created_at: Optional[datetime] = None

    description: Optional[str] = None
    """# Description"""

    api_model_role_id: Optional[str] = FieldInfo(alias="model_role_id", default=None)
    """# Model Role ID"""

    updated_at: Optional[datetime] = None
