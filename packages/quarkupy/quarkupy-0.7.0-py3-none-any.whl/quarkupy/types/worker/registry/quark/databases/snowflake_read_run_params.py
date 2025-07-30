# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["SnowflakeReadRunParams", "Auth"]


class SnowflakeReadRunParams(TypedDict, total=False):
    account: Required[str]
    """Snowflake Account ID"""

    auth: Required[Auth]
    """Authentication Details"""

    lattice_id: Required[str]

    query: Required[str]

    opt_database: str
    """Snowflake Database"""

    opt_role: str
    """Executing Role"""

    opt_schema: str
    """Snowflake Schema"""

    opt_warehouse: str
    """Snowflake Warehouse"""


class Auth(TypedDict, total=False):
    password: Required[str]

    username: Required[str]
