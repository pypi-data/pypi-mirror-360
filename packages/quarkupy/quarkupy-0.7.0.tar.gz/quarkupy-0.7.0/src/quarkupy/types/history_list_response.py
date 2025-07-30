# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List

from .._models import BaseModel
from .history.flow_history_item import FlowHistoryItem
from .history.quark_history_item import QuarkHistoryItem

__all__ = ["HistoryListResponse"]


class HistoryListResponse(BaseModel):
    lattices: List[FlowHistoryItem]

    quarks: List[QuarkHistoryItem]
