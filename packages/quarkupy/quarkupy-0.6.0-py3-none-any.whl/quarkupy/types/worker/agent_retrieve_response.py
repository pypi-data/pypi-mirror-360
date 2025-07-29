# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["AgentRetrieveResponse", "Agent", "AgentFlowAgent"]


class AgentFlowAgent(BaseModel):
    id: str


class Agent(BaseModel):
    id: str

    flow_agent: AgentFlowAgent
    """REST API representation of the [FlowAgent]"""

    name: str

    status: Literal["New", "Running", "Stopped", "Paused", "Error"]

    description: Optional[str] = None


class AgentRetrieveResponse(BaseModel):
    agents: List[Agent]
