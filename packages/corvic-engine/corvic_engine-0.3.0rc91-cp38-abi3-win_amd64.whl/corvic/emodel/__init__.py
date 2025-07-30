"""Data modeling objects for creating corvic pipelines."""

import corvic.emodel._feature_type as feature_type
from corvic import transfer
from corvic.emodel._base_model import (
    BelongsToOrgModelMixin,
    BelongsToRoomModelMixin,
    HasIdOrmBackedModel,
    NoIdModel,
    OrgWideStandardModel,
    OrmBelongsToRoomT,
    OrmHasIdBelongsToOrgT,
    OrmHasIdBelongsToRoomT,
    ProtoBelongsToOrgT,
    ProtoBelongsToRoomT,
    ProtoHasIdBelongsToOrgT,
    ProtoHasIdBelongsToRoomT,
    StandardModel,
)
from corvic.emodel._data_connector import DataConnector, DataConnectorID
from corvic.emodel._feature_view import (
    Column,
    DeepGnnCsvUrlMetadata,
    FeatureView,
    FeatureViewEdgeTableMetadata,
    FeatureViewRelationshipsMetadata,
)
from corvic.emodel._pipeline import (
    ChunkPdfsPipeline,
    OcrPdfsPipeline,
    Pipeline,
    PipelineID,
    SanitizeParquetPipeline,
    SpecificPipeline,
    UnknownTransformationPipeline,
)
from corvic.emodel._proto_orm_convert import (
    add_orm_org_mixin_to_session,
    add_orm_room_mixin_to_session,
    space_orm_to_proto,
    timestamp_orm_to_proto,
)
from corvic.emodel._resource import (
    Resource,
    ResourceID,
)
from corvic.emodel._room import (
    Room,
    RoomID,
)
from corvic.emodel._source import Source, SourceID
from corvic.emodel._space import (
    ConcatAndEmbedParameters,
    EmbedAndConcatParameters,
    EmbedImageParameters,
    ImageSpace,
    Node2VecParameters,
    RelationalSpace,
    SemanticSpace,
    Space,
    SpecificSpace,
    SpecificSpaceParameters,
    TabularSpace,
    UnknownSpace,
    embedding_model_proto_to_name,
    image_model_can_embed_images,
    image_model_can_embed_text,
    image_model_proto_to_name,
)

FeatureType = feature_type.FeatureType
OrmIdT = transfer.OrmIdT

__all__ = [
    "BelongsToOrgModelMixin",
    "BelongsToRoomModelMixin",
    "ChunkPdfsPipeline",
    "Column",
    "ConcatAndEmbedParameters",
    "DataConnector",
    "DataConnectorID",
    "DeepGnnCsvUrlMetadata",
    "EmbedAndConcatParameters",
    "EmbedImageParameters",
    "FeatureType",
    "FeatureView",
    "FeatureViewEdgeTableMetadata",
    "FeatureViewRelationshipsMetadata",
    "HasIdOrmBackedModel",
    "ImageSpace",
    "NoIdModel",
    "Node2VecParameters",
    "OcrPdfsPipeline",
    "OrgWideStandardModel",
    "OrmBelongsToRoomT",
    "OrmHasIdBelongsToOrgT",
    "OrmHasIdBelongsToRoomT",
    "OrmIdT",
    "Pipeline",
    "PipelineID",
    "ProtoBelongsToOrgT",
    "ProtoBelongsToRoomT",
    "ProtoHasIdBelongsToOrgT",
    "ProtoHasIdBelongsToRoomT",
    "RelationalSpace",
    "Resource",
    "ResourceID",
    "Room",
    "RoomID",
    "SanitizeParquetPipeline",
    "SemanticSpace",
    "Source",
    "SourceID",
    "Space",
    "SpecificPipeline",
    "SpecificSpace",
    "SpecificSpaceParameters",
    "StandardModel",
    "TabularSpace",
    "UnknownSpace",
    "UnknownTransformationPipeline",
    "add_orm_org_mixin_to_session",
    "add_orm_room_mixin_to_session",
    "embedding_model_proto_to_name",
    "feature_type",
    "image_model_can_embed_images",
    "image_model_can_embed_text",
    "image_model_proto_to_name",
    "space_orm_to_proto",
    "timestamp_orm_to_proto",
]
