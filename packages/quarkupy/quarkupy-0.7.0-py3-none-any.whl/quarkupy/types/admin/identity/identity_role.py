# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime

from ...._models import BaseModel
from .identity_model import IdentityModel

__all__ = ["IdentityRole"]


class IdentityRole(BaseModel):
    identities: List[IdentityModel]

    name: str

    role_id: str

    created_at: Optional[datetime] = None

    description: Optional[str] = None

    owner: Optional[IdentityModel] = None

    updated_at: Optional[datetime] = None
