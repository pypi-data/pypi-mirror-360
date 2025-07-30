from __future__ import annotations

import copy
from collections.abc import Iterable, Sequence
from datetime import datetime
from typing import Literal, Self, TypeAlias

from corvic import eorm, system, transfer
from corvic.emodel._base_model import OrgWideStandardModel
from corvic.emodel._proto_orm_convert import (
    data_connector_delete_orms,
    data_connector_orm_to_proto,
    data_connector_proto_to_orm,
)
from corvic.result import InvalidArgumentError, NotFoundError, Ok
from corvic_generated.model.v1alpha import models_pb2
from corvic_generated.orm.v1 import data_connector_pb2

DataConnectorID: TypeAlias = eorm.DataConnectorID
OrgID: TypeAlias = eorm.OrgID


class DataConnector(
    OrgWideStandardModel[DataConnectorID, models_pb2.DataConnector, eorm.DataConnector],
):
    """Data Connector Model."""

    @classmethod
    def orm_class(cls):
        return eorm.DataConnector

    @classmethod
    def id_class(cls):
        return DataConnectorID

    @classmethod
    def orm_to_proto(cls, orm_obj: eorm.DataConnector) -> models_pb2.DataConnector:
        return data_connector_orm_to_proto(orm_obj)

    @classmethod
    def proto_to_orm(
        cls, proto_obj: models_pb2.DataConnector, session: eorm.Session
    ) -> Ok[eorm.DataConnector] | InvalidArgumentError:
        return data_connector_proto_to_orm(proto_obj, session)

    @classmethod
    def delete_by_ids(
        cls, ids: Sequence[DataConnectorID], session: eorm.Session
    ) -> Ok[None] | InvalidArgumentError:
        return data_connector_delete_orms(ids, session)

    @property
    def name(self) -> str:
        return self.proto_self.name

    @property
    def provider(self) -> Literal["s3", "azure-blob", "gcs"] | None:
        match self.proto_self.parameters.WhichOneof("credentials"):
            case "azure_blob_credentials":
                return "azure-blob"
            case "s3_credentials":
                return "s3"
            case "gcs_credentials":
                return "gcs"
            case _:
                return None

    @property
    def parameters(
        self,
    ) -> (
        data_connector_pb2.AzureBlobCredentials
        | data_connector_pb2.S3Credentials
        | data_connector_pb2.GCSCredentials
        | None
    ):
        match self.provider:
            case "azure-blob":
                return self.azure_blob_credentials
            case "s3":
                return self.s3_credentials
            case "gcs":
                return self.gcs_credentials
            case None:
                return None

    @property
    def azure_blob_credentials(
        self,
    ) -> data_connector_pb2.AzureBlobCredentials | None:
        if self.proto_self.parameters.HasField("azure_blob_credentials"):
            return self.proto_self.parameters.azure_blob_credentials
        return None

    @property
    def s3_credentials(
        self,
    ) -> data_connector_pb2.S3Credentials | None:
        if self.proto_self.parameters.HasField("s3_credentials"):
            return self.proto_self.parameters.s3_credentials
        return None

    @property
    def gcs_credentials(
        self,
    ) -> data_connector_pb2.GCSCredentials | None:
        if self.proto_self.parameters.HasField("gcs_credentials"):
            return self.proto_self.parameters.gcs_credentials
        return None

    @property
    def base_path(self) -> str:
        return self.proto_self.base_path

    @property
    def secret_key(self) -> str:
        return self.proto_self.secret_key

    @property
    def last_validation_time(self) -> datetime | None:
        return transfer.non_empty_timestamp_to_datetime(
            self.proto_self.last_validation_time
        )

    @property
    def last_successful_validation(self) -> datetime | None:
        return transfer.non_empty_timestamp_to_datetime(
            self.proto_self.last_successful_validation
        )

    @property
    def is_validated(self) -> bool:
        return (
            self.last_successful_validation is not None
            and self.last_validation_time is not None
            and self.last_successful_validation >= self.last_validation_time
        )

    @classmethod
    def create(
        cls,
        *,
        name: str,
        parameters: data_connector_pb2.DataConnectorParameters,
        base_path: str,
        secret_key: str,
        client: system.Client,
    ):
        return cls(
            proto_self=models_pb2.DataConnector(
                name=name,
                parameters=parameters,
                base_path=base_path,
                secret_key=secret_key,
            ),
            client=client,
        )

    @classmethod
    def list(
        cls,
        *,
        limit: int | None = None,
        created_before: datetime | None = None,
        ids: Iterable[DataConnectorID] | None = None,
        existing_session: eorm.Session | None = None,
        client: system.Client,
    ) -> Ok[list[Self]] | NotFoundError | InvalidArgumentError:
        """List access models."""
        match cls.list_as_proto(
            limit=limit,
            created_before=created_before,
            ids=ids,
            existing_session=existing_session,
            client=client,
        ):
            case NotFoundError() | InvalidArgumentError() as err:
                return err
            case Ok(protos):
                return Ok(
                    [
                        cls.from_proto(
                            proto=proto,
                            client=client,
                        )
                        for proto in protos
                    ]
                )

    @classmethod
    def from_proto(
        cls,
        *,
        proto: models_pb2.DataConnector,
        client: system.Client,
    ) -> Self:
        return cls(
            proto_self=proto,
            client=client,
        )

    @classmethod
    def from_id(
        cls,
        *,
        data_connector_id: DataConnectorID,
        session: eorm.Session | None = None,
        client: system.Client,
    ) -> Ok[Self] | NotFoundError:
        return cls.load_proto_for(
            obj_id=data_connector_id,
            client=client,
            existing_session=session,
        ).map(
            lambda proto_self: cls.from_proto(
                proto=proto_self,
                client=client,
            )
        )

    def with_name(self, name: str) -> DataConnector:
        proto_self = copy.deepcopy(self.proto_self)
        proto_self.name = name
        return DataConnector(
            proto_self=proto_self,
            client=self.client,
        )

    def with_parameters(
        self, parameters: data_connector_pb2.DataConnectorParameters
    ) -> DataConnector:
        proto_self = copy.deepcopy(self.proto_self)
        proto_self.parameters.CopyFrom(parameters)
        return DataConnector(
            proto_self=proto_self,
            client=self.client,
        )

    def with_base_path(self, base_path: str) -> DataConnector:
        proto_self = copy.deepcopy(self.proto_self)
        proto_self.base_path = base_path
        return DataConnector(
            proto_self=proto_self,
            client=self.client,
        )

    def with_secret_key(self, secret_key: str) -> DataConnector:
        proto_self = copy.deepcopy(self.proto_self)
        proto_self.secret_key = secret_key
        return DataConnector(
            proto_self=proto_self,
            client=self.client,
        )

    def with_last_validation_time(
        self, last_validation_time: datetime
    ) -> DataConnector:
        proto_self = copy.deepcopy(self.proto_self)
        proto_self.last_validation_time.FromDatetime(last_validation_time)
        return DataConnector(
            proto_self=proto_self,
            client=self.client,
        )

    def with_last_successful_validation(
        self, last_successful_validation: datetime
    ) -> DataConnector:
        proto_self = copy.deepcopy(self.proto_self)
        proto_self.last_successful_validation.FromDatetime(last_successful_validation)
        return DataConnector(
            proto_self=proto_self,
            client=self.client,
        )
