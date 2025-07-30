# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Required, TypedDict

__all__ = ["SchemaInfoParam", "Field"]


class Field(TypedDict, total=False):
    data_type: Required[str]

    name: Required[str]

    description: str


class SchemaInfoParam(TypedDict, total=False):
    extra_fields_allowed: Required[bool]

    fields: Required[Iterable[Field]]
