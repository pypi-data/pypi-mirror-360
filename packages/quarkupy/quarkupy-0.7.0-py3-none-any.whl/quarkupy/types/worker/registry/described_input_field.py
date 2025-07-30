# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ...._models import BaseModel
from .schema_info import SchemaInfo

__all__ = ["DescribedInputField"]


class DescribedInputField(BaseModel):
    advanced: bool

    field_name: str

    field_type: str

    friendly_name: str

    required: bool

    sensitive: bool

    default_value: Optional[object] = None

    description: Optional[str] = None

    ipc_schema: Optional[SchemaInfo] = None
    """API-Friendly representation of a [Schema]"""
