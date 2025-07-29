# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from datetime import datetime
from typing_extensions import Literal, Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["SourceUpdatePartialParams"]


class SourceUpdatePartialParams(TypedDict, total=False):
    config: Required[object]

    config_type: Required[Literal["S3ObjectStore", "Other"]]

    name: Required[str]

    owned_by_identity_id: Required[str]

    source_type: Required[Literal["Files", "Database", "Other"]]

    status: Required[Literal["SetupInProgress", "SetupComplete", "Other"]]

    description: str

    updated_at: Annotated[Union[str, datetime], PropertyInfo(format="iso8601")]
