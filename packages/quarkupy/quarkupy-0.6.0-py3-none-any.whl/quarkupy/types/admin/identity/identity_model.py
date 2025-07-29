# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime
from typing_extensions import Literal

from ...._models import BaseModel

__all__ = ["IdentityModel"]


class IdentityModel(BaseModel):
    disabled: bool

    email_verified: bool

    external: bool

    identity_id: str

    identity_type: Literal["User", "SystemInternal", "SystemExternal"]

    username: str

    avatar_url: Optional[str] = None

    created_at: Optional[datetime] = None

    display_name: Optional[str] = None

    email: Optional[str] = None

    external_id: Optional[str] = None

    external_updated_at: Optional[datetime] = None

    last_login: Optional[datetime] = None

    updated_at: Optional[datetime] = None
