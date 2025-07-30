# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List
from typing_extensions import TypeAlias

from .identity_role import IdentityRole

__all__ = ["RoleListResponse"]

RoleListResponse: TypeAlias = List[IdentityRole]
