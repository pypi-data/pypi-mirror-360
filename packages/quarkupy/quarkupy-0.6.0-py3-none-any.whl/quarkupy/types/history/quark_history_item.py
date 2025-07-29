# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["QuarkHistoryItem"]


class QuarkHistoryItem(BaseModel):
    created_at: datetime
    """The timestamp indicating when the Quark was created."""

    flow_history_id: str
    """Identifier of the associated Flow."""

    identity_id: str
    """Identity of Quark runner"""

    input: object
    """Input data associated with the Quark, stored as a JSON value."""

    output: object
    """Output data produced by the Quark execution, stored as a JSON value."""

    quark_history_id: str
    """Unique identifier for the Quark."""

    registry_qrn: str
    """
    User-facing fully qualified identifier for the registry where the Quark is
    defined.
    """

    state: object
    """Quark State"""

    status: Literal["New", "Scheduled", "Running", "OutputStaged", "Completed", "Failed"]
    """Represents the status/stage of a Quark instance"""

    registry_id: Optional[str] = None
    """Registry ID of the database entry"""

    runner_task_id: Optional[str] = None
    """Runner [WorkerTask] id Optional, as there are stages when no runner is assigned"""

    supervisor_task_id: Optional[str] = None
    """
    Supervisor [WorkerTask] id Optional, as there are stages when no supervisor is
    assigned
    """

    worker_id: Optional[str] = None
    """Runner [WorkerTask] id Optional, as there are stages when no worker is assigned"""
