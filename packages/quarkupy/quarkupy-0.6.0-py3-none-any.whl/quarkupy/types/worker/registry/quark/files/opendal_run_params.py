# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Union
from typing_extensions import Literal, Required, TypeAlias, TypedDict

from .quark_file_object_status import QuarkFileObjectStatus

__all__ = [
    "OpendalRunParams",
    "Config",
    "ConfigOpendalConfigInputOpendalS3Config",
    "ConfigOpendalConfigInputOpendalMemoryConfig",
    "ConfigOpendalConfigInputOpendalGDriveConfig",
    "ConfigOpendalConfigInputOpendalOneDriveConfig",
]


class OpendalRunParams(TypedDict, total=False):
    config: Required[Config]
    """OpenAPI compatible set of configs"""

    flow_id: Required[str]

    source_id: Required[str]

    opt_paths: List[str]
    """Filter read by paths (directories or files)"""

    opt_recursive: bool

    opt_set_status: QuarkFileObjectStatus


class ConfigOpendalConfigInputOpendalS3Config(TypedDict, total=False):
    bucket: Required[str]
    """bucket name of this backend.

    required.
    """

    type: Required[Literal["S3"]]

    access_key_id: str
    """access_key_id of this backend.

    - If access_key_id is set, we will take user's input first.
    - If not, we will try to load it from environment.
    """

    allow_anonymous: bool
    """
    Allow anonymous will allow opendal to send request without signing when
    credential is not loaded.
    """

    batch_max_operations: int
    """Set maximum batch operations of this backend.

    Some compatible services have a limit on the number of operations in a batch
    request. For example, R2 could return `Internal Error` while batch delete 1000
    files.

    Please tune this value based on services' document.
    """

    checksum_algorithm: str
    """
    Checksum Algorithm to use when sending checksums in HTTP headers. This is
    necessary when writing to AWS S3 Buckets with Object Lock enabled for example.

    Available options:

    - "crc32c"
    """

    default_storage_class: str
    """default storage_class for this backend.

    Available values:

    - `DEEP_ARCHIVE`
    - `GLACIER`
    - `GLACIER_IR`
    - `INTELLIGENT_TIERING`
    - `ONEZONE_IA`
    - `EXPRESS_ONEZONE`
    - `OUTPOSTS`
    - `REDUCED_REDUNDANCY`
    - `STANDARD`
    - `STANDARD_IA`

    S3 compatible services don't support all of them
    """

    delete_max_size: int
    """Set the maximum delete size of this backend.

    Some compatible services have a limit on the number of operations in a batch
    request. For example, R2 could return `Internal Error` while batch delete 1000
    files.

    Please tune this value based on services' document.
    """

    disable_config_load: bool
    """Disable config load so that opendal will not load config from environment.

    For examples:

    - envs like `AWS_ACCESS_KEY_ID`
    - files like `~/.aws/config`
    """

    disable_ec2_metadata: bool
    """Disable load credential from ec2 metadata.

    This option is used to disable the default behavior of opendal to load
    credential from ec2 metadata, a.k.a, IMDSv2
    """

    disable_list_objects_v2: bool
    """
    OpenDAL uses List Objects V2 by default to list objects. However, some legacy
    services do not yet support V2. This option allows users to switch back to the
    older List Objects V1.
    """

    disable_stat_with_override: bool
    """
    Disable stat with override so that opendal will not send stat request with
    override queries.

    For example, R2 doesn't support stat with `response_content_type` query.
    """

    disable_write_with_if_match: bool
    """
    Disable write with if match so that opendal will not send write request with if
    match headers.

    For example, Ceph RADOS S3 doesn't support write with if match.
    """

    enable_request_payer: bool
    """
    Indicates whether the client agrees to pay for the requests made to the S3
    bucket.
    """

    enable_versioning: bool
    """# Bucket versioning"""

    enable_virtual_host_style: bool
    """
    Enable virtual host style so that opendal will send API requests in virtual host
    style instead of path style.

    - By default, opendal will send API to
      `https://s3.us-east-1.amazonaws.com/bucket_name`
    - Enabled, opendal will send API to
      `https://bucket_name.s3.us-east-1.amazonaws.com`
    """

    enable_write_with_append: bool
    """
    Enable write with append so that opendal will send write request with append
    headers.
    """

    endpoint: str
    """endpoint of this backend.

    Endpoint must be full uri, e.g.

    - AWS S3: `https://s3.amazonaws.com` or `https://s3.{region}.amazonaws.com`
    - Cloudflare R2: `https://<ACCOUNT_ID>.r2.cloudflarestorage.com`
    - Aliyun OSS: `https://{region}.aliyuncs.com`
    - Tencent COS: `https://cos.{region}.myqcloud.com`
    - Minio: `http://127.0.0.1:9000`

    If user inputs endpoint without scheme like "s3.amazonaws.com", we will prepend
    "https://" before it.

    - If endpoint is set, we will take user's input first.
    - If not, we will try to load it from environment.
    - If still not set, default to `https://s3.amazonaws.com`.
    """

    external_id: str
    """external_id for this backend."""

    region: str
    """Region represent the signing region of this endpoint.

    This is required if you are using the default AWS S3 endpoint.

    If using a custom endpoint,

    - If region is set, we will take user's input first.
    - If not, we will try to load it from environment.
    """

    role_arn: str
    """role_arn for this backend.

    If `role_arn` is set, we will use already known config as source credential to
    assume role with `role_arn`.
    """

    role_session_name: str
    """role_session_name for this backend."""

    root: str
    """# Root Path

    All operations will happen under this root (relative
    """

    secret_access_key: str
    """secret_access_key of this backend.

    - If secret_access_key is set, we will take user's input first.
    - If not, we will try to load it from environment.
    """

    server_side_encryption: str
    """server_side_encryption for this backend.

    Available values: `AES256`, `aws:kms`.
    """

    server_side_encryption_aws_kms_key_id: str
    """server_side_encryption_aws_kms_key_id for this backend

    - If `server_side_encryption` set to `aws:kms`, and
      `server_side_encryption_aws_kms_key_id` is not set, S3 will use aws managed
      kms key to encrypt data.
    - If `server_side_encryption` set to `aws:kms`, and
      `server_side_encryption_aws_kms_key_id` is a valid kms key id, S3 will use the
      provided kms key to encrypt data.
    - If the `server_side_encryption_aws_kms_key_id` is invalid or not found, an
      error will be returned.
    - If `server_side_encryption` is not `aws:kms`, setting
      `server_side_encryption_aws_kms_key_id` is a noop.
    """

    server_side_encryption_customer_algorithm: str
    """server_side_encryption_customer_algorithm for this backend.

    Available values: `AES256`.
    """

    server_side_encryption_customer_key: str
    """server_side_encryption_customer_key for this backend.

    Value: BASE64-encoded key that matches algorithm specified in
    `server_side_encryption_customer_algorithm`.
    """

    server_side_encryption_customer_key_md5: str
    """Set server_side_encryption_customer_key_md5 for this backend.

    Value: MD5 digest of key specified in `server_side_encryption_customer_key`.
    """

    session_token: str
    """session_token (aka, security token) of this backend.

    This token will expire after sometime, it's recommended to set session_token by
    hand.
    """


class ConfigOpendalConfigInputOpendalMemoryConfig(TypedDict, total=False):
    type: Required[Literal["Mem"]]

    root: str
    """root of the backend."""


class ConfigOpendalConfigInputOpendalGDriveConfig(TypedDict, total=False):
    type: Required[Literal["GDrive"]]

    access_token: str
    """Access token for gdrive."""

    client_id: str
    """Client id for gdrive."""

    client_secret: str
    """Client secret for gdrive."""

    refresh_token: str
    """Refresh token for gdrive."""

    root: str
    """The root for gdrive"""


class ConfigOpendalConfigInputOpendalOneDriveConfig(TypedDict, total=False):
    type: Required[Literal["OneDrive"]]

    access_token: str
    """Microsoft Graph API (also OneDrive API) access token"""

    client_id: str
    """
    Microsoft Graph API Application (client) ID that is in the Azure's app
    registration portal
    """

    client_secret: str
    """
    Microsoft Graph API Application client secret that is in the Azure's app
    registration portal
    """

    enable_versioning: bool
    """Enabling version support"""

    refresh_token: str
    """Microsoft Graph API (also OneDrive API) refresh token"""

    root: str
    """The root path for the OneDrive service for the file access"""


Config: TypeAlias = Union[
    ConfigOpendalConfigInputOpendalS3Config,
    ConfigOpendalConfigInputOpendalMemoryConfig,
    ConfigOpendalConfigInputOpendalGDriveConfig,
    ConfigOpendalConfigInputOpendalOneDriveConfig,
]
