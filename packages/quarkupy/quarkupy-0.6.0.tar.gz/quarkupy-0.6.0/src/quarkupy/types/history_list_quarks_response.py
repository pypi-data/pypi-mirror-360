# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List
from typing_extensions import TypeAlias

from .history.quark_history_item import QuarkHistoryItem

__all__ = ["HistoryListQuarksResponse"]

HistoryListQuarksResponse: TypeAlias = List[QuarkHistoryItem]
