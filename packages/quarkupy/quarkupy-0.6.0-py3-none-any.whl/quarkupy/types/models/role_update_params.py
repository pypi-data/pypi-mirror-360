# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from datetime import datetime
from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["RoleUpdateParams"]


class RoleUpdateParams(TypedDict, total=False):
    config_override: Required[object]
    """# Optional Override for Model Configuration"""

    model_id: Required[str]
    """# Associated Model"""

    name: Required[str]
    """# Model Role Name"""

    owned_by_identity_id: Required[str]
    """# Model Role Owner"""

    description: str
    """# Description"""

    updated_at: Annotated[Union[str, datetime], PropertyInfo(format="iso8601")]
