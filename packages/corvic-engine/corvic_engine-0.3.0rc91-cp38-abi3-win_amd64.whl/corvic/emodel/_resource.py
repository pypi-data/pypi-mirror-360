"""Resources."""

from __future__ import annotations

import copy
import datetime
import uuid
from collections.abc import Iterable, Sequence
from typing import Self, TypeAlias

import polars as pl
import sqlalchemy as sa
from sqlalchemy import orm as sa_orm
from sqlalchemy.orm.interfaces import LoaderOption

from corvic import eorm, system
from corvic.emodel._base_model import StandardModel
from corvic.emodel._defaults import Defaults
from corvic.emodel._proto_orm_convert import (
    resource_delete_orms,
    resource_orm_to_proto,
    resource_proto_to_orm,
)
from corvic.result import InternalError, InvalidArgumentError, NotFoundError, Ok
from corvic_generated.model.v1alpha import models_pb2
from corvic_generated.status.v1 import event_pb2

SourceID: TypeAlias = eorm.SourceID
ResourceID: TypeAlias = eorm.ResourceID
RoomID: TypeAlias = eorm.RoomID
PipelineID: TypeAlias = eorm.PipelineID


class Resource(StandardModel[ResourceID, models_pb2.Resource, eorm.Resource]):
    """Resources represent import data."""

    @classmethod
    def orm_class(cls):
        return eorm.Resource

    @classmethod
    def id_class(cls):
        return ResourceID

    @classmethod
    def orm_to_proto(cls, orm_obj: eorm.Resource) -> models_pb2.Resource:
        return resource_orm_to_proto(orm_obj)

    @classmethod
    def proto_to_orm(
        cls, proto_obj: models_pb2.Resource, session: eorm.Session
    ) -> Ok[eorm.Resource] | InvalidArgumentError:
        return resource_proto_to_orm(proto_obj, session)

    @classmethod
    def delete_by_ids(
        cls, ids: Sequence[ResourceID], session: eorm.Session
    ) -> Ok[None] | InvalidArgumentError:
        return resource_delete_orms(ids, session)

    @property
    def url(self) -> str:
        return self.proto_self.url

    @property
    def name(self) -> str:
        return self.proto_self.name

    @property
    def pipeline_id(self) -> PipelineID | None:
        return PipelineID(self.proto_self.pipeline_id) or None

    @property
    def mime_type(self) -> str:
        return self.proto_self.mime_type

    @property
    def md5(self) -> str:
        return self.proto_self.md5

    @property
    def size(self) -> int:
        return self.proto_self.size

    @property
    def original_path(self) -> str:
        return self.proto_self.original_path

    @property
    def description(self) -> str:
        return self.proto_self.description

    @property
    def latest_event(self) -> event_pb2.Event | None:
        return (
            self.proto_self.recent_events[-1] if self.proto_self.recent_events else None
        )

    @property
    def is_terminal(self) -> bool:
        if self.proto_self.is_terminal:
            return True
        if not self.latest_event:
            return False
        return self.latest_event.event_type in [
            event_pb2.EVENT_TYPE_FINISHED,
            event_pb2.EVENT_TYPE_ERROR,
        ]

    def with_event(self, event: event_pb2.Event) -> Resource:
        new_proto = copy.copy(self.proto_self)
        new_proto.recent_events.append(event)
        new_proto.is_terminal = event.event_type in [
            event_pb2.EVENT_TYPE_FINISHED,
            event_pb2.EVENT_TYPE_ERROR,
        ]
        return Resource(
            proto_self=new_proto,
            client=self.client,
        )

    @classmethod
    def orm_load_options(cls) -> list[LoaderOption]:
        return [
            sa_orm.selectinload(eorm.Resource.pipeline_ref).selectinload(
                eorm.PipelineInput.resource
            ),
        ]

    @classmethod
    def list(  # noqa: PLR0913
        cls,
        *,
        room_id: RoomID | None = None,
        pipeline_id: PipelineID | None = None,
        limit: int | None = None,
        created_before: datetime.datetime | None = None,
        ids: Iterable[ResourceID] | None = None,
        is_terminal: bool | None = None,
        existing_session: eorm.Session | None = None,
        url: str | None = None,
        client: system.Client,
    ) -> Ok[list[Resource]] | NotFoundError | InvalidArgumentError:
        """List resources."""

        def query_transform(query: sa.Select[tuple[eorm.Resource]]):
            if url:
                query = query.where(eorm.Resource.url == url)
            if pipeline_id:
                query = query.where(
                    eorm.Resource.id.in_(
                        sa.select(eorm.PipelineInput.resource_id).where(
                            eorm.PipelineInput.pipeline_id == pipeline_id
                        )
                    )
                )
            match is_terminal:
                case True:
                    query = query.where(eorm.Resource.is_terminal.is_(True))
                case False:
                    query = query.where(
                        sa.or_(
                            eorm.Resource.is_terminal.is_(False),
                            eorm.Resource.is_terminal.is_(None),
                        )
                    )
                case None:
                    pass
            return query

        match cls.list_as_proto(
            client=client,
            limit=limit,
            room_id=room_id,
            created_before=created_before,
            ids=ids,
            existing_session=existing_session,
            additional_query_transform=query_transform,
        ):
            case NotFoundError() | InvalidArgumentError() as err:
                return err
            case Ok(protos):
                return Ok(
                    [cls.from_proto(proto=proto, client=client) for proto in protos]
                )

    @classmethod
    def from_proto(
        cls,
        *,
        proto: models_pb2.Resource,
        client: system.Client,
    ) -> Resource:
        return cls(proto_self=proto, client=client)

    @classmethod
    def from_id(
        cls,
        *,
        resource_id: ResourceID,
        session: eorm.Session | None = None,
        client: system.Client,
    ) -> Ok[Resource] | NotFoundError:
        return cls.load_proto_for(
            obj_id=resource_id,
            client=client,
            existing_session=session,
        ).map(
            lambda proto_self: cls.from_proto(
                proto=proto_self,
                client=client,
            )
        )

    @classmethod
    def from_blob(
        cls,
        *,
        name: str,
        blob: system.Blob,
        original_path: str = "",
        description: str = "",
        room_id: eorm.RoomID | None = None,
        client: system.Client,
    ) -> Self:
        room_id = room_id or Defaults.get_default_room_id(client=client)
        blob.reload()
        md5 = blob.md5_hash
        size = blob.size

        if not md5 or not size:
            raise InternalError("failed to get metadata from blob store")

        proto_resource = models_pb2.Resource(
            name=name,
            mime_type=blob.content_type,
            url=blob.url,
            md5=md5,
            size=size,
            original_path=original_path,
            description=description,
            room_id=str(room_id),
            recent_events=[],
        )
        return cls(client=client, proto_self=proto_resource)

    @classmethod
    def from_polars(
        cls,
        *,
        dataframe: pl.DataFrame,
        room_id: eorm.RoomID | None = None,
        client: system.Client,
    ) -> Self:
        room_id = room_id or Defaults.get_default_room_id(client=client)

        blob = client.storage_manager.make_tabular_blob(
            room_id, f"polars_dataframe/{uuid.uuid4()}"
        )
        with blob.open(mode="wb") as stream:
            dataframe.write_parquet(stream)

        blob.content_type = "application/octet-stream"
        blob.patch()
        return cls.from_blob(
            name=blob.url,
            blob=blob,
            client=client,
            room_id=room_id,
        )

    def as_input_to(self, pipeline_id: eorm.PipelineID) -> Resource:
        proto_self = copy.deepcopy(self.proto_self)
        proto_self.pipeline_id = str(pipeline_id)
        proto_self.pipeline_input_name = f"output-{uuid.uuid4()}"
        return Resource(proto_self=proto_self, client=self.client)

    @property
    def pipeline_input_name(self) -> str:
        return self.proto_self.pipeline_input_name
