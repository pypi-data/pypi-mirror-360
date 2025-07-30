# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["LancedbIngestRunParams"]


class LancedbIngestRunParams(TypedDict, total=False):
    ipc_dataset_id: Required[str]

    lattice_id: Required[str]

    table_name: Required[str]

    opt_operation: str

    opt_uri: str
