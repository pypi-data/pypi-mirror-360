# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["AgentChatRagDemoParams"]


class AgentChatRagDemoParams(TypedDict, total=False):
    openai_api_key: Required[str]

    query: Required[str]

    table_name: Required[str]

    search_limit: int
