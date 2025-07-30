# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime
from typing_extensions import TypeAlias

from ..._models import BaseModel

__all__ = ["APIKeyListResponse", "APIKeyListResponseItem"]


class APIKeyListResponseItem(BaseModel):
    active: bool
    """# Active"""

    created_at: datetime

    identity_api_key_id: str
    """# Key ID"""

    identity_id: str
    """# Identity"""

    name: str
    """# Key Name"""

    prefix: str
    """# Key Prefix"""

    updated_at: datetime

    expires_at: Optional[datetime] = None
    """# Expiration Date"""


APIKeyListResponse: TypeAlias = List[APIKeyListResponseItem]
