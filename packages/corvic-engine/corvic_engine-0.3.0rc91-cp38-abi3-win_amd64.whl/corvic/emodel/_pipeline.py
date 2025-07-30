from __future__ import annotations

import copy
import dataclasses
import datetime
import functools
import uuid
from collections.abc import Iterable, Mapping, Sequence
from typing import Self, TypeAlias, cast

import polars as pl
from sqlalchemy import orm as sa_orm
from sqlalchemy.orm.interfaces import LoaderOption

import corvic.table
from corvic import eorm, op_graph, system
from corvic.emodel._base_model import StandardModel
from corvic.emodel._defaults import Defaults
from corvic.emodel._proto_orm_convert import (
    pipeline_delete_orms,
    pipeline_orm_to_proto,
    pipeline_proto_to_orm,
)
from corvic.emodel._source import Source
from corvic.result import InvalidArgumentError, NotFoundError, Ok, UnavailableError
from corvic_generated.model.v1alpha import models_pb2
from corvic_generated.orm.v1 import pipeline_pb2

PipelineID: TypeAlias = eorm.PipelineID
RoomID: TypeAlias = eorm.RoomID


class Pipeline(StandardModel[PipelineID, models_pb2.Pipeline, eorm.Pipeline]):
    """Pipelines map resources to sources."""

    @classmethod
    def orm_class(cls):
        return eorm.Pipeline

    @classmethod
    def id_class(cls):
        return PipelineID

    @classmethod
    def orm_to_proto(cls, orm_obj: eorm.Pipeline) -> models_pb2.Pipeline:
        return pipeline_orm_to_proto(orm_obj)

    @classmethod
    def proto_to_orm(
        cls, proto_obj: models_pb2.Pipeline, session: eorm.Session
    ) -> Ok[eorm.Pipeline] | InvalidArgumentError:
        return pipeline_proto_to_orm(proto_obj, session)

    @classmethod
    def delete_by_ids(
        cls, ids: Sequence[PipelineID], session: eorm.Session
    ) -> Ok[None] | InvalidArgumentError:
        return pipeline_delete_orms(ids, session)

    @classmethod
    def _create(
        cls,
        *,
        pipeline_name: str,
        description: str,
        room_id: RoomID,
        source_outputs: dict[str, Source],
        transformation: pipeline_pb2.PipelineTransformation,
        client: system.Client,
    ) -> Self:
        proto_pipeline = models_pb2.Pipeline(
            name=pipeline_name,
            room_id=str(room_id),
            source_outputs={
                output_name: source.proto_self
                for output_name, source in source_outputs.items()
            },
            pipeline_transformation=transformation,
            description=description,
        )
        return cls(proto_self=proto_pipeline, client=client)

    @classmethod
    def from_proto(
        cls, *, proto: models_pb2.Pipeline, client: system.Client
    ) -> SpecificPipeline:
        if proto.pipeline_transformation.HasField("ocr_pdf"):
            return OcrPdfsPipeline(proto_self=proto, client=client)

        if proto.pipeline_transformation.HasField("chunk_pdf"):
            return ChunkPdfsPipeline(proto_self=proto, client=client)

        if proto.pipeline_transformation.HasField("sanitize_parquet"):
            return SanitizeParquetPipeline(proto_self=proto, client=client)

        return UnknownTransformationPipeline(proto_self=proto, client=client)

    @classmethod
    def from_id(
        cls,
        *,
        pipeline_id: PipelineID,
        session: eorm.Session | None = None,
        client: system.Client,
    ) -> Ok[SpecificPipeline] | NotFoundError:
        match cls.list_as_proto(
            limit=1, ids=[pipeline_id], client=client, existing_session=session
        ):
            case Ok(proto_list):
                return (
                    Ok(
                        cls.from_proto(
                            proto=proto_list[0],
                            client=client,
                        )
                    )
                    if proto_list
                    else NotFoundError(
                        "object with given id does not exist", id=pipeline_id
                    )
                )
            case NotFoundError() as err:
                return err
            case InvalidArgumentError() as err:
                return NotFoundError.from_(err)

    @classmethod
    def orm_load_options(cls) -> list[LoaderOption]:
        return [
            sa_orm.selectinload(eorm.Pipeline.outputs)
            .selectinload(eorm.PipelineOutput.source)
            .selectinload(eorm.Source.pipeline_ref),
        ]

    @classmethod
    def list(
        cls,
        *,
        limit: int | None = None,
        room_id: RoomID | None = None,
        created_before: datetime.datetime | None = None,
        ids: Iterable[PipelineID] | None = None,
        existing_session: eorm.Session | None = None,
        client: system.Client,
    ) -> Ok[list[SpecificPipeline]] | InvalidArgumentError | NotFoundError:
        match cls.list_as_proto(
            client=client,
            limit=limit,
            room_id=room_id,
            created_before=created_before,
            ids=ids,
            existing_session=existing_session,
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

    @property
    def name(self):
        return self.proto_self.name

    @property
    def description(self):
        return self.proto_self.description

    @functools.cached_property
    def outputs(self) -> Mapping[str, Source]:
        return {
            name: Source(
                proto_self=proto_source,
                client=self.client,
            )
            for name, proto_source in self.proto_self.source_outputs.items()
        }

    def with_name(self, name: str) -> Pipeline:
        proto_self = copy.deepcopy(self.proto_self)
        proto_self.name = name
        return Pipeline(
            proto_self=proto_self,
            client=self.client,
        )


class UnknownTransformationPipeline(Pipeline):
    """A pipeline that this version of the code doesn't know what to do with."""


@dataclasses.dataclass
class NewColumn:
    name: str
    dtype: pl.DataType
    ftype: op_graph.FeatureType


def _add_columns_to_source(
    source: Source, columns: list[NewColumn]
) -> Ok[Source] | InvalidArgumentError:
    source_op_graph: op_graph.Op = source.table.op_graph
    for col in columns:
        match source_op_graph.add_column(
            pl.Series(name=col.name, values=[], dtype=col.dtype), col.ftype
        ):
            case InvalidArgumentError() as err:
                return err
            case Ok(val):
                source_op_graph = cast(op_graph.Op, val)

    return Ok(
        source.with_table(corvic.table.Table.from_ops(source.client, source_op_graph))
    )


class ChunkPdfsPipeline(Pipeline):
    @classmethod
    def create(
        cls,
        *,
        pipeline_name: str,
        source_name: str,
        description: str = "",
        room_id: RoomID | None = None,
        client: system.Client,
    ) -> Ok[Self] | InvalidArgumentError:
        """Create a pipeline for parsing PDFs into text chunks."""
        room_id = room_id or Defaults.get_default_room_id(client=client)
        match Source.create(name=source_name, client=client, room_id=room_id).and_then(
            lambda s: _add_columns_to_source(
                s,
                [
                    NewColumn("id", pl.String(), op_graph.feature_type.primary_key()),
                    NewColumn("text", pl.String(), op_graph.feature_type.text()),
                    NewColumn(
                        "metadata_json", pl.String(), op_graph.feature_type.text()
                    ),
                    NewColumn("index", pl.Int32(), op_graph.feature_type.identifier()),
                ],
            )
        ):
            case InvalidArgumentError() as err:
                return err
            case Ok(source):
                pass

        output_name = f"output-{uuid.uuid4()}"
        return Ok(
            cls._create(
                pipeline_name=pipeline_name,
                description=description,
                room_id=room_id,
                source_outputs={output_name: source},
                transformation=pipeline_pb2.PipelineTransformation(
                    chunk_pdf=pipeline_pb2.ChunkPdfPipelineTransformation(
                        output_name=output_name
                    )
                ),
                client=client,
            )
        )

    @property
    def output_name(self):
        return self.proto_self.pipeline_transformation.chunk_pdf.output_name

    @property
    def output_source(self):
        return self.outputs[self.output_name]


class OcrPdfsPipeline(Pipeline):
    @classmethod
    def create(
        cls,
        *,
        pipeline_name: str,
        text_source_name: str,
        relationship_source_name: str,
        image_source_name: str,
        description: str = "",
        room_id: RoomID | None = None,
        client: system.Client,
    ) -> Ok[Self] | InvalidArgumentError | UnavailableError:
        """Create a pipeline for using OCR to process PDFs into structured sources."""
        room_id = room_id or Defaults.get_default_room_id(client=client)
        match (
            Source.create(name=text_source_name, client=client, room_id=room_id)
            .and_then(
                lambda s: _add_columns_to_source(
                    s,
                    [
                        NewColumn(
                            "id", pl.String(), op_graph.feature_type.primary_key()
                        ),
                        NewColumn("content", pl.String(), op_graph.feature_type.text()),
                        NewColumn(
                            "document",
                            pl.String(),
                            op_graph.feature_type.text(),
                        ),
                        NewColumn(
                            "type",
                            pl.String(),
                            op_graph.feature_type.categorical(),
                        ),
                        NewColumn("title", pl.String(), op_graph.feature_type.text()),
                        NewColumn(
                            "resource_id",
                            pl.String(),
                            op_graph.feature_type.identifier(),
                        ),
                        NewColumn(
                            "page_number",
                            pl.Int64(),
                            op_graph.feature_type.numerical(),
                        ),
                        NewColumn(
                            "bbox",
                            pl.Struct(
                                [
                                    pl.Field("x1", pl.Float64()),
                                    pl.Field("y1", pl.Float64()),
                                    pl.Field("x2", pl.Float64()),
                                    pl.Field("y2", pl.Float64()),
                                ]
                            ),
                            op_graph.feature_type.embedding(),
                        ),
                        NewColumn(
                            "created_at",
                            pl.Datetime(),
                            op_graph.feature_type.timestamp(),
                        ),
                    ],
                )
            )
            .and_then(lambda s: s.commit())
        ):
            case InvalidArgumentError() | UnavailableError() as err:
                return err
            case Ok(text_source):
                pass

        match (
            Source.create(name=relationship_source_name, client=client, room_id=room_id)
            .and_then(
                lambda s: _add_columns_to_source(
                    s,
                    [
                        NewColumn(
                            "from",
                            pl.String(),
                            op_graph.feature_type.foreign_key(text_source.id),
                        ),
                        NewColumn(
                            "to",
                            pl.String(),
                            op_graph.feature_type.foreign_key(text_source.id),
                        ),
                        NewColumn(
                            "type",
                            pl.String(),
                            op_graph.feature_type.categorical(),
                        ),
                    ],
                )
            )
            .and_then(lambda s: s.commit())
        ):
            case InvalidArgumentError() | UnavailableError() as err:
                return err
            case Ok(relationship_source):
                pass

        match (
            Source.create(name=image_source_name, client=client, room_id=room_id)
            .and_then(
                lambda s: _add_columns_to_source(
                    s,
                    [
                        NewColumn(
                            "id", pl.String(), op_graph.feature_type.primary_key()
                        ),
                        NewColumn(
                            "content", pl.Binary(), op_graph.feature_type.image()
                        ),
                        NewColumn(
                            "description", pl.String(), op_graph.feature_type.text()
                        ),
                        NewColumn(
                            "document",
                            pl.String(),
                            op_graph.feature_type.text(),
                        ),
                        NewColumn("title", pl.String(), op_graph.feature_type.text()),
                        NewColumn(
                            "text_id",
                            pl.String(),
                            op_graph.feature_type.foreign_key(text_source.id),
                        ),
                        NewColumn(
                            "resource_id",
                            pl.String(),
                            op_graph.feature_type.identifier(),
                        ),
                        NewColumn(
                            "page_number",
                            pl.Int64(),
                            op_graph.feature_type.numerical(),
                        ),
                        NewColumn(
                            "bbox",
                            pl.Struct(
                                [
                                    pl.Field("x1", pl.Float64()),
                                    pl.Field("y1", pl.Float64()),
                                    pl.Field("x2", pl.Float64()),
                                    pl.Field("y2", pl.Float64()),
                                ]
                            ),
                            op_graph.feature_type.embedding(),
                        ),
                        NewColumn(
                            "created_at",
                            pl.Datetime(),
                            op_graph.feature_type.timestamp(),
                        ),
                    ],
                )
            )
            .and_then(lambda s: s.commit())
        ):
            case InvalidArgumentError() | UnavailableError() as err:
                return err
            case Ok(image_source):
                pass

        text_output_name = f"text_output-{uuid.uuid4()}"
        relationship_output_name = f"relationship_output-{uuid.uuid4()}"
        image_output_name = f"image_output-{uuid.uuid4()}"
        return Ok(
            cls._create(
                pipeline_name=pipeline_name,
                description=description,
                room_id=room_id,
                source_outputs={
                    text_output_name: text_source,
                    relationship_output_name: relationship_source,
                    image_output_name: image_source,
                },
                transformation=pipeline_pb2.PipelineTransformation(
                    ocr_pdf=pipeline_pb2.OcrPdfPipelineTransformation(
                        text_output_name=text_output_name,
                        relationship_output_name=relationship_output_name,
                        image_output_name=image_output_name,
                    )
                ),
                client=client,
            )
        )

    @property
    def text_output_name(self):
        return self.proto_self.pipeline_transformation.ocr_pdf.text_output_name

    @property
    def relationship_output_name(self):
        return self.proto_self.pipeline_transformation.ocr_pdf.relationship_output_name

    @property
    def image_output_name(self):
        return self.proto_self.pipeline_transformation.ocr_pdf.image_output_name

    @property
    def text_output_source(self):
        return self.outputs[self.text_output_name]

    @property
    def relationship_output_source(self):
        return self.outputs[self.relationship_output_name]

    @property
    def image_output_source(self):
        return self.outputs[self.image_output_name]


class SanitizeParquetPipeline(Pipeline):
    @classmethod
    def create(
        cls,
        *,
        pipeline_name: str,
        source_name: str,
        room_id: RoomID | None = None,
        description: str = "",
        client: system.Client,
    ) -> Ok[Self] | InvalidArgumentError:
        """Create a pipeline for parsing PDFs into text chunks."""
        room_id = room_id or Defaults.get_default_room_id(client=client)
        match Source.create(name=source_name, client=client, room_id=room_id):
            case InvalidArgumentError() as err:
                return err
            case Ok(source):
                pass

        output_name = f"output-{uuid.uuid4()}"
        return Ok(
            cls._create(
                pipeline_name=pipeline_name,
                description=description,
                room_id=room_id,
                source_outputs={output_name: source},
                transformation=pipeline_pb2.PipelineTransformation(
                    sanitize_parquet=pipeline_pb2.SanitizeParquetPipelineTransformation(
                        output_name=output_name
                    )
                ),
                client=client,
            )
        )

    @property
    def output_name(self):
        return self.proto_self.pipeline_transformation.sanitize_parquet.output_name

    @property
    def output_source(self):
        return self.outputs[self.output_name]


SpecificPipeline: TypeAlias = (
    ChunkPdfsPipeline
    | OcrPdfsPipeline
    | SanitizeParquetPipeline
    | UnknownTransformationPipeline
)
