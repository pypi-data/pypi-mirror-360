# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Optional
from datetime import datetime
from typing_extensions import Literal

from .quark_tag import QuarkTag
from ...._models import BaseModel
from .schema_info import SchemaInfo
from .described_input_field import DescribedInputField

__all__ = ["LatticeRegistryItem", "Edge", "Node"]


class Edge(BaseModel):
    source_node_id: str

    target_node_id: str


class Node(BaseModel):
    constants: Dict[str, object]

    lattice_to_quark_input_map: Dict[str, str]

    name: str

    node_id: str

    quark_reg_id: str

    description: Optional[str] = None


class LatticeRegistryItem(BaseModel):
    author: str

    created_at: datetime

    edges: List[Edge]

    flow_registry_id: str

    hidden: bool

    identifier: str

    inputs: List[DescribedInputField]

    lattice_type: Literal["Ingest", "Inference", "Other"]

    name: str

    nodes: List[Node]

    tags: List[QuarkTag]

    version: str

    description: Optional[str] = None

    output_schema: Optional[SchemaInfo] = None
    """API-Friendly representation of a [Schema]"""

    updated_at: Optional[datetime] = None
