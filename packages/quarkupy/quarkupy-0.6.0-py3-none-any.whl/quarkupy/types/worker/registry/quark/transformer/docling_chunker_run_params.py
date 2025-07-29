# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Required, TypedDict

__all__ = ["DoclingChunkerRunParams"]


class DoclingChunkerRunParams(TypedDict, total=False):
    ipc_dataset_id: Required[str]

    lattice_id: Required[str]

    opt_drop_cols: List[str]

    opt_max_tokens: int

    opt_merge_peers: bool

    opt_model: str

    opt_text_col: str
