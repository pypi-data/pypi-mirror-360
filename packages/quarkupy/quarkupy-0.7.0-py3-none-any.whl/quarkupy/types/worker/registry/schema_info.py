# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ...._models import BaseModel

__all__ = ["SchemaInfo", "Field"]


class Field(BaseModel):
    data_type: str

    name: str

    description: Optional[str] = None


class SchemaInfo(BaseModel):
    extra_fields_allowed: bool

    fields: List[Field]
