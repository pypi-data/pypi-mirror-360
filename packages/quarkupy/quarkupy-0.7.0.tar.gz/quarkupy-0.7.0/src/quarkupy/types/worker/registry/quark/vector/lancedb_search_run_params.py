# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Iterable
from typing_extensions import Literal, Required, TypeAlias, TypedDict

__all__ = [
    "LancedbSearchRunParams",
    "Query",
    "QuerySimpleInputValueSimpleInputTextSearch",
    "QuerySimpleInputValueSimpleInputEmbeddingSearch",
    "QuerySimpleInputValueSimpleInputPlainText",
]


class LancedbSearchRunParams(TypedDict, total=False):
    lattice_id: Required[str]

    query: Required[Query]
    """Represents the simple input a Quark/Lattice - usually used for inference

    TODO: Replace this with
    [Issue 23](https://github.com/ProjectBifrost/bifrost/issues/23)
    """

    table_name: Required[str]

    opt_uri: str


class QuerySimpleInputValueSimpleInputTextSearch(TypedDict, total=False):
    criteria: Required[str]

    type: Required[Literal["TextSearch"]]

    limit: int


class QuerySimpleInputValueSimpleInputEmbeddingSearch(TypedDict, total=False):
    criteria: Required[Iterable[float]]

    type: Required[Literal["EmbeddingSearch"]]

    limit: int


class QuerySimpleInputValueSimpleInputPlainText(TypedDict, total=False):
    text: Required[str]

    type: Required[Literal["PlainText"]]


Query: TypeAlias = Union[
    QuerySimpleInputValueSimpleInputTextSearch,
    QuerySimpleInputValueSimpleInputEmbeddingSearch,
    QuerySimpleInputValueSimpleInputPlainText,
]
