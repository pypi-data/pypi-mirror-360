# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List
from typing_extensions import TypeAlias

from .history.flow_history_item import FlowHistoryItem

__all__ = ["HistoryListFlowsResponse"]

HistoryListFlowsResponse: TypeAlias = List[FlowHistoryItem]
