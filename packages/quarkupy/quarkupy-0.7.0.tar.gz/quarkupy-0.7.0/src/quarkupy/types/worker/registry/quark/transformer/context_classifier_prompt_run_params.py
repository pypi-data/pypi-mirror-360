# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Required, TypedDict

__all__ = ["ContextClassifierPromptRunParams"]


class ContextClassifierPromptRunParams(TypedDict, total=False):
    classifier_ids: Required[List[str]]

    flow_id: Required[str]

    ipc_dataset_id: Required[str]

    opt_rendered_col: str
