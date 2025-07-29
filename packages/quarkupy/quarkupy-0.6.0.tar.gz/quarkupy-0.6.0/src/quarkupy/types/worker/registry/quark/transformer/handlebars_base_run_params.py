# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Required, TypedDict

__all__ = ["HandlebarsBaseRunParams"]


class HandlebarsBaseRunParams(TypedDict, total=False):
    input_columns: Required[List[str]]

    ipc_dataset_id: Required[str]

    lattice_id: Required[str]

    template: Required[str]

    opt_rendered_col: str
