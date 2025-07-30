# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["SourceCreateParams", "Config"]


class SourceCreateParams(TypedDict, total=False):
    config: Required[Config]

    name: Required[str]

    description: str


class Config(TypedDict, total=False):
    access_key_id: Required[str]

    endpoint: Required[str]

    region: Required[str]

    secret_access_key: Required[str]

    url: Required[str]
