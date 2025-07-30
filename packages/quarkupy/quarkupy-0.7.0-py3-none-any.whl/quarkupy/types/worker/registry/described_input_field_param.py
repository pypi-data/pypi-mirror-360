# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

from .schema_info_param import SchemaInfoParam

__all__ = ["DescribedInputFieldParam"]


class DescribedInputFieldParam(TypedDict, total=False):
    advanced: Required[bool]

    field_name: Required[str]

    field_type: Required[str]

    friendly_name: Required[str]

    required: Required[bool]

    sensitive: Required[bool]

    default_value: object

    description: str

    ipc_schema: SchemaInfoParam
    """API-Friendly representation of a [Schema]"""
