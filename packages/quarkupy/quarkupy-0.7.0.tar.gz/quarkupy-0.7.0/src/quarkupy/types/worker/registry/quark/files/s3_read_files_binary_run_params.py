# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["S3ReadFilesBinaryRunParams"]


class S3ReadFilesBinaryRunParams(TypedDict, total=False):
    access_key_id: Required[str]

    access_key_secret: Required[str]

    lattice_id: Required[str]

    url: Required[str]

    opt_bucket: str

    opt_enable_http: bool

    opt_endpoint: str

    opt_region: str
