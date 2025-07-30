from buf.validate import validate_pb2 as _validate_pb2
from corvic_generated.status.v1 import event_pb2 as _event_pb2
from google.protobuf import descriptor_pb2 as _descriptor_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class PipelineType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    PIPELINE_TYPE_UNSPECIFIED: _ClassVar[PipelineType]
    PIPELINE_TYPE_PROCESS_PDFS: _ClassVar[PipelineType]
    PIPELINE_TYPE_PROCESS_PARQUET: _ClassVar[PipelineType]
    PIPELINE_TYPE_PROCESS_PDFS_OCR: _ClassVar[PipelineType]
PIPELINE_TYPE_UNSPECIFIED: PipelineType
PIPELINE_TYPE_PROCESS_PDFS: PipelineType
PIPELINE_TYPE_PROCESS_PARQUET: PipelineType
PIPELINE_TYPE_PROCESS_PDFS_OCR: PipelineType

class CreatePipelineRequest(_message.Message):
    __slots__ = ("pipeline_name", "room_id", "pipeline_type", "pipeline_description")
    PIPELINE_NAME_FIELD_NUMBER: _ClassVar[int]
    ROOM_ID_FIELD_NUMBER: _ClassVar[int]
    PIPELINE_TYPE_FIELD_NUMBER: _ClassVar[int]
    PIPELINE_DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    pipeline_name: str
    room_id: str
    pipeline_type: PipelineType
    pipeline_description: str
    def __init__(self, pipeline_name: _Optional[str] = ..., room_id: _Optional[str] = ..., pipeline_type: _Optional[_Union[PipelineType, str]] = ..., pipeline_description: _Optional[str] = ...) -> None: ...

class PipelineEntry(_message.Message):
    __slots__ = ("pipeline_id", "pipeline_name", "room_id", "pipeline_type", "input_resource_ids", "output_source_ids", "created_at", "recent_events", "pipeline_description")
    PIPELINE_ID_FIELD_NUMBER: _ClassVar[int]
    PIPELINE_NAME_FIELD_NUMBER: _ClassVar[int]
    ROOM_ID_FIELD_NUMBER: _ClassVar[int]
    PIPELINE_TYPE_FIELD_NUMBER: _ClassVar[int]
    INPUT_RESOURCE_IDS_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_SOURCE_IDS_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    RECENT_EVENTS_FIELD_NUMBER: _ClassVar[int]
    PIPELINE_DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    pipeline_id: str
    pipeline_name: str
    room_id: str
    pipeline_type: PipelineType
    input_resource_ids: _containers.RepeatedScalarFieldContainer[str]
    output_source_ids: _containers.RepeatedScalarFieldContainer[str]
    created_at: _timestamp_pb2.Timestamp
    recent_events: _containers.RepeatedCompositeFieldContainer[_event_pb2.Event]
    pipeline_description: str
    def __init__(self, pipeline_id: _Optional[str] = ..., pipeline_name: _Optional[str] = ..., room_id: _Optional[str] = ..., pipeline_type: _Optional[_Union[PipelineType, str]] = ..., input_resource_ids: _Optional[_Iterable[str]] = ..., output_source_ids: _Optional[_Iterable[str]] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., recent_events: _Optional[_Iterable[_Union[_event_pb2.Event, _Mapping]]] = ..., pipeline_description: _Optional[str] = ...) -> None: ...

class CreatePipelineResponse(_message.Message):
    __slots__ = ("pipeline_entry",)
    PIPELINE_ENTRY_FIELD_NUMBER: _ClassVar[int]
    pipeline_entry: PipelineEntry
    def __init__(self, pipeline_entry: _Optional[_Union[PipelineEntry, _Mapping]] = ...) -> None: ...

class DeletePipelineRequest(_message.Message):
    __slots__ = ("pipeline_id",)
    PIPELINE_ID_FIELD_NUMBER: _ClassVar[int]
    pipeline_id: str
    def __init__(self, pipeline_id: _Optional[str] = ...) -> None: ...

class DeletePipelineResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetPipelineRequest(_message.Message):
    __slots__ = ("pipeline_id",)
    PIPELINE_ID_FIELD_NUMBER: _ClassVar[int]
    pipeline_id: str
    def __init__(self, pipeline_id: _Optional[str] = ...) -> None: ...

class GetPipelineResponse(_message.Message):
    __slots__ = ("pipeline_entry",)
    PIPELINE_ENTRY_FIELD_NUMBER: _ClassVar[int]
    pipeline_entry: PipelineEntry
    def __init__(self, pipeline_entry: _Optional[_Union[PipelineEntry, _Mapping]] = ...) -> None: ...

class ListPipelinesCursorPayload(_message.Message):
    __slots__ = ("create_time_of_last_entry",)
    CREATE_TIME_OF_LAST_ENTRY_FIELD_NUMBER: _ClassVar[int]
    create_time_of_last_entry: _timestamp_pb2.Timestamp
    def __init__(self, create_time_of_last_entry: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class ListPipelinesRequest(_message.Message):
    __slots__ = ("room_id", "entries_per_page", "cursor")
    ROOM_ID_FIELD_NUMBER: _ClassVar[int]
    ENTRIES_PER_PAGE_FIELD_NUMBER: _ClassVar[int]
    CURSOR_FIELD_NUMBER: _ClassVar[int]
    room_id: str
    entries_per_page: int
    cursor: str
    def __init__(self, room_id: _Optional[str] = ..., entries_per_page: _Optional[int] = ..., cursor: _Optional[str] = ...) -> None: ...

class ListPipelinesResponse(_message.Message):
    __slots__ = ("pipeline_entries", "cursor")
    PIPELINE_ENTRIES_FIELD_NUMBER: _ClassVar[int]
    CURSOR_FIELD_NUMBER: _ClassVar[int]
    pipeline_entries: _containers.RepeatedCompositeFieldContainer[PipelineEntry]
    cursor: str
    def __init__(self, pipeline_entries: _Optional[_Iterable[_Union[PipelineEntry, _Mapping]]] = ..., cursor: _Optional[str] = ...) -> None: ...
