# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime
from typing_extensions import Literal

from .quark_tag import QuarkTag
from ...._models import BaseModel
from .schema_info import SchemaInfo
from .described_input_field import DescribedInputField

__all__ = ["QuarkRegistryItem"]


class QuarkRegistryItem(BaseModel):
    author: str

    category: Literal["AI", "Api", "Database", "Extractor", "Files", "Transformer", "Vector", "Other"]

    created_at: datetime

    hidden: bool

    name: str

    node_type: Literal["Input", "Output", "InputOutput"]

    qrn: str

    quark_registry_id: str

    tags: List[QuarkTag]

    version: str

    description: Optional[str] = None

    inputs: Optional[List[DescribedInputField]] = None

    output_schema: Optional[SchemaInfo] = None
    """API-Friendly representation of a [Schema]"""

    updated_at: Optional[datetime] = None
