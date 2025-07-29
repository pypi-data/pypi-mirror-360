# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["Source"]


class Source(BaseModel):
    config: object

    config_type: Literal["S3ObjectStore", "Other"]

    created_at: datetime

    name: str

    owned_by_identity_id: str

    source_id: str

    source_type: Literal["Files", "Database", "Other"]

    status: Literal["SetupInProgress", "SetupComplete", "Other"]

    description: Optional[str] = None

    updated_at: Optional[datetime] = None
