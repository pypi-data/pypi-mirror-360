from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class S3Credentials(_message.Message):
    __slots__ = ("access_key_id", "region")
    ACCESS_KEY_ID_FIELD_NUMBER: _ClassVar[int]
    REGION_FIELD_NUMBER: _ClassVar[int]
    access_key_id: str
    region: str
    def __init__(self, access_key_id: _Optional[str] = ..., region: _Optional[str] = ...) -> None: ...

class GCSCredentials(_message.Message):
    __slots__ = ("service_account_json",)
    SERVICE_ACCOUNT_JSON_FIELD_NUMBER: _ClassVar[int]
    service_account_json: str
    def __init__(self, service_account_json: _Optional[str] = ...) -> None: ...

class AzureBlobCredentials(_message.Message):
    __slots__ = ("account_url",)
    ACCOUNT_URL_FIELD_NUMBER: _ClassVar[int]
    account_url: str
    def __init__(self, account_url: _Optional[str] = ...) -> None: ...

class DataConnectorParameters(_message.Message):
    __slots__ = ("s3_credentials", "gcs_credentials", "azure_blob_credentials")
    S3_CREDENTIALS_FIELD_NUMBER: _ClassVar[int]
    GCS_CREDENTIALS_FIELD_NUMBER: _ClassVar[int]
    AZURE_BLOB_CREDENTIALS_FIELD_NUMBER: _ClassVar[int]
    s3_credentials: S3Credentials
    gcs_credentials: GCSCredentials
    azure_blob_credentials: AzureBlobCredentials
    def __init__(self, s3_credentials: _Optional[_Union[S3Credentials, _Mapping]] = ..., gcs_credentials: _Optional[_Union[GCSCredentials, _Mapping]] = ..., azure_blob_credentials: _Optional[_Union[AzureBlobCredentials, _Mapping]] = ...) -> None: ...
