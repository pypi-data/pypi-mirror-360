# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ...._models import BaseModel
from .lattice_react_flow_pos import LatticeReactFlowPos

__all__ = ["LatticeRetrieveFlowResponse", "Edge", "Node", "NodeData", "NodePosition"]


class Edge(BaseModel):
    id: str
    """A unique identifier for the edge."""

    animated: bool
    """A boolean indicating whether this edge has an animation effect."""

    source: str
    """The identifier of the source node this edge connects from."""

    target: str
    """The identifier of the target node this edge connects to."""

    type: str

    style: Optional[object] = None
    """Optional style properties for customizing the edge's appearance."""


class NodeData(BaseModel):
    label: str
    """The label displayed for the node."""


class NodePosition(BaseModel):
    x: int
    """The horizontal position (in pixels)."""

    y: int
    """The vertical position (in pixels)."""


class Node(BaseModel):
    id: str
    """A unique identifier for the node."""

    data: NodeData
    """Represents the data for a React Flow Node in the Lattice graph.

    # Fields

    - `label` - The label displayed for the node.
    """

    position: NodePosition
    """Represents the position of a React Flow Node in the Lattice graph.

    # Fields

    - `x` - The horizontal position (in pixels).
    - `y` - The vertical position (in pixels).
    """

    source_handle_position: LatticeReactFlowPos
    """Source Handle Position"""

    target_handle_position: LatticeReactFlowPos
    """Target Handle Position"""

    type: str
    """The type of the node (serialized as "type")."""

    style: Optional[object] = None
    """Optional style properties for configuring the appearance of the node."""


class LatticeRetrieveFlowResponse(BaseModel):
    description: str
    """A brief description of the graph."""

    edges: List[Edge]
    """A list of edges connecting the nodes in the graph."""

    name: str
    """The name of the graph."""

    nodes: List[Node]
    """A list of nodes in the graph."""
