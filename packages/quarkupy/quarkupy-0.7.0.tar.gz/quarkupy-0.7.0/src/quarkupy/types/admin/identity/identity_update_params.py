# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["IdentityUpdateParams"]


class IdentityUpdateParams(TypedDict, total=False):
    disabled: Required[bool]

    identity_type: Required[Literal["User", "SystemInternal", "SystemExternal"]]

    username: Required[str]

    display_name: str

    email: str

    password: str
