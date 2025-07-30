# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["OpenAICompletionBaseRunParams"]


class OpenAICompletionBaseRunParams(TypedDict, total=False):
    api_key: Required[str]

    ipc_dataset_id: Required[str]

    lattice_id: Required[str]

    opt_explode_json: bool

    opt_json_output: bool

    opt_max_output_tokens: int

    opt_model_name: str

    opt_prompt_column: str

    opt_system_prompt: str
