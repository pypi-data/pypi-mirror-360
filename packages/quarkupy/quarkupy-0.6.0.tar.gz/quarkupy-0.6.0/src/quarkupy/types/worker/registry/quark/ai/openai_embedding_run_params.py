# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Required, TypedDict

__all__ = ["OpenAIEmbeddingRunParams"]


class OpenAIEmbeddingRunParams(TypedDict, total=False):
    api_key: Required[str]

    ipc_dataset_id: Required[str]

    lattice_id: Required[str]

    opt_model_name: str

    opt_num_embeddings: int

    opt_text_additional_embed_columns: List[str]

    opt_text_column_name: str
