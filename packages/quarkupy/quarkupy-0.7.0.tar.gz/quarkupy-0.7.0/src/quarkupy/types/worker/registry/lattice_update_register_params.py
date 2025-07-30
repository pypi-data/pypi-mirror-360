# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, List, Iterable
from typing_extensions import Literal, Required, TypedDict

from .quark_tag import QuarkTag
from .schema_info_param import SchemaInfoParam
from .described_input_field_param import DescribedInputFieldParam

__all__ = ["LatticeUpdateRegisterParams", "Edge", "Node"]


class LatticeUpdateRegisterParams(TypedDict, total=False):
    author: Required[str]

    edges: Required[Iterable[Edge]]

    flow_registry_id: Required[str]

    hidden: Required[bool]

    identifier: Required[str]

    inputs: Required[Iterable[DescribedInputFieldParam]]

    lattice_type: Required[Literal["Ingest", "Inference", "Other"]]

    name: Required[str]

    nodes: Required[Iterable[Node]]

    tags: Required[List[QuarkTag]]

    version: Required[str]

    description: str

    output_schema: SchemaInfoParam
    """API-Friendly representation of a [Schema]"""


class Edge(TypedDict, total=False):
    source_node_id: Required[str]

    target_node_id: Required[str]


class Node(TypedDict, total=False):
    constants: Required[Dict[str, object]]

    lattice_to_quark_input_map: Required[Dict[str, str]]

    name: Required[str]

    node_id: Required[str]

    quark_reg_id: Required[str]

    description: str
