# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["ManagementRetrieveResponse", "Task"]


class Task(BaseModel):
    is_finished: bool

    task_id: str

    task_type: str

    task_type_id: str

    parent_task_id: Optional[str] = None

    task_name: Optional[str] = None


class ManagementRetrieveResponse(BaseModel):
    id: str

    data_port: int

    host: str

    joined_at: str

    last_seen_at: str

    management_port: int

    num_task_workers: int

    status: Literal["New", "Available", "Busy", "Error"]
    """Server statuses for workers and slots

    - [WorkerSlotStatus::New] Created but uninitialized
    - [WorkerSlotStatus::Available] Ready to accept work
    - [WorkerSlotStatus::Busy] Currently performing work, and not currently
      available for additional work
    - [WorkerSlotStatus::Error] In an error state and not available for work
    """

    tasks: List[Task]

    tls: bool

    updated_at: str

    version: str

    error_message: Optional[str] = None
