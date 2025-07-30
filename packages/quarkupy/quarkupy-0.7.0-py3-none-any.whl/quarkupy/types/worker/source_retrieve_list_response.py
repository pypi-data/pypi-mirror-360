# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Optional
from datetime import datetime

from ..._models import BaseModel
from .registry.quark.files.quark_file_object_status import QuarkFileObjectStatus

__all__ = ["SourceRetrieveListResponse", "Object"]


class Object(BaseModel):
    date_added: datetime

    extra: Dict[str, str]

    file_id: str

    file_name: str

    last_scanned: datetime

    origin_quark: str

    path: str

    source_id: str

    status: QuarkFileObjectStatus

    binary: Optional[List[int]] = None

    cache_control: Optional[str] = None

    content_disposition: Optional[str] = None

    content_encoding: Optional[str] = None

    content_length: Optional[int] = None

    content_range: Optional[str] = None

    content_type: Optional[str] = None

    deleted_at_source: Optional[bool] = None

    e_tag: Optional[str] = None
    """
    The unique identifier for the object
    <https://datatracker.ietf.org/doc/html/rfc9110#name-etag>
    """

    images: Optional[List[str]] = None

    markdown: Optional[str] = None

    source_is_current: Optional[bool] = None

    source_last_modified: Optional[datetime] = None

    source_version: Optional[str] = None
    """A version indicator for this object"""


class SourceRetrieveListResponse(BaseModel):
    objects: List[Object]

    prefixes: List[str]

    relative_path: str

    root_path: str
