# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from .._models import BaseModel
from .worker.registry.schema_info import SchemaInfo

__all__ = ["DataSetInfo", "Batch"]


class Batch(BaseModel):
    id: str

    bytes: int

    created_at: datetime

    records: int

    status: str

    sent_completed_at: Optional[datetime] = None

    status_error_message: Optional[str] = None


class DataSetInfo(BaseModel):
    id: str

    batches: List[Batch]

    bytes: int

    created_at: datetime

    ordered: bool

    records: int

    schema_: SchemaInfo = FieldInfo(alias="schema")
    """API-Friendly representation of a [Schema]"""

    status: Literal[
        "New",
        "Empty",
        "Pending",
        "Sending",
        "Received",
        "Available",
        "Consumed",
        "SenderError",
        "ReceiverError",
        "GeneralError",
    ]
    """Represents the status/stage of a Quark instance The status of a dataset

    - [DatasetStatus::New] Created but unpopulated
    - [DatasetStatus::Empty] Created but no records
    - [DatasetStatus::Available] Ready to be consumed
    - [DatasetStatus::Sending] Currently being sent to worker
    - [DatasetStatus::Busy] Currently being consumed or populated
    - [DatasetStatus::Consumed] Consumed and no longer available
    - [DatasetStatus::Error] In an error state and not available
    """

    completed_at: Optional[datetime] = None

    consumer_quarks: Optional[List[str]] = None

    destroyed_at: Optional[datetime] = None

    source_quark_id: Optional[str] = None

    status_error_message: Optional[str] = None
