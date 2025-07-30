# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["ContextInsertSegmentRunParams"]


class ContextInsertSegmentRunParams(TypedDict, total=False):
    flow_id: Required[str]

    ipc_dataset_id: Required[str]
