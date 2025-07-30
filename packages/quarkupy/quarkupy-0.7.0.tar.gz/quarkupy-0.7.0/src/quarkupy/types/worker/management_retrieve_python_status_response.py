# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List

from ..._models import BaseModel

__all__ = ["ManagementRetrievePythonStatusResponse"]


class ManagementRetrievePythonStatusResponse(BaseModel):
    exec_prefix: str
    """Python exec prefix"""

    modules: List[str]
    """Available modules"""

    path: List[str]
    """Python path"""

    prefix: str
    """Python path prefix"""

    site: List[str]
    """Python site"""

    version: str
    """Python version"""
