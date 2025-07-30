# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from datetime import datetime
from typing_extensions import Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["HistoryListFlowsParams"]


class HistoryListFlowsParams(TypedDict, total=False):
    max_timestamp: Annotated[Union[str, datetime], PropertyInfo(format="iso8601")]

    min_timestamp: Annotated[Union[str, datetime], PropertyInfo(format="iso8601")]

    registry_identifier: str
