# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List

from ..._models import BaseModel
from .registry.quark_registry_item import QuarkRegistryItem
from .registry.lattice_registry_item import LatticeRegistryItem

__all__ = ["RegistryListResponse"]


class RegistryListResponse(BaseModel):
    lattices: List[LatticeRegistryItem]
    """A list of all Lattices in the registry."""

    lattices_suffix: str
    """The suffix used for Lattice-related API endpoints."""

    quarks: List[QuarkRegistryItem]
    """A list of all Quarks in the registry."""

    quarks_suffix: str
    """The suffix used for Quark-related API endpoints."""

    root_url: str
    """The base URL of the API."""
