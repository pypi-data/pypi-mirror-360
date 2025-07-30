from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class AddRecordRequest(_message.Message):
    __slots__ = ("data_source_code", "record_id", "record_definition", "flags")
    DATA_SOURCE_CODE_FIELD_NUMBER: _ClassVar[int]
    RECORD_ID_FIELD_NUMBER: _ClassVar[int]
    RECORD_DEFINITION_FIELD_NUMBER: _ClassVar[int]
    FLAGS_FIELD_NUMBER: _ClassVar[int]
    data_source_code: str
    record_id: str
    record_definition: str
    flags: int
    def __init__(self, data_source_code: _Optional[str] = ..., record_id: _Optional[str] = ..., record_definition: _Optional[str] = ..., flags: _Optional[int] = ...) -> None: ...

class AddRecordResponse(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: str
    def __init__(self, result: _Optional[str] = ...) -> None: ...

class CloseExportReportRequest(_message.Message):
    __slots__ = ("export_handle",)
    EXPORT_HANDLE_FIELD_NUMBER: _ClassVar[int]
    export_handle: int
    def __init__(self, export_handle: _Optional[int] = ...) -> None: ...

class CloseExportReportResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class CountRedoRecordsRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class CountRedoRecordsResponse(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: int
    def __init__(self, result: _Optional[int] = ...) -> None: ...

class DeleteRecordRequest(_message.Message):
    __slots__ = ("data_source_code", "record_id", "flags")
    DATA_SOURCE_CODE_FIELD_NUMBER: _ClassVar[int]
    RECORD_ID_FIELD_NUMBER: _ClassVar[int]
    FLAGS_FIELD_NUMBER: _ClassVar[int]
    data_source_code: str
    record_id: str
    flags: int
    def __init__(self, data_source_code: _Optional[str] = ..., record_id: _Optional[str] = ..., flags: _Optional[int] = ...) -> None: ...

class DeleteRecordResponse(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: str
    def __init__(self, result: _Optional[str] = ...) -> None: ...

class ExportCsvEntityReportRequest(_message.Message):
    __slots__ = ("csv_column_list", "flags")
    CSV_COLUMN_LIST_FIELD_NUMBER: _ClassVar[int]
    FLAGS_FIELD_NUMBER: _ClassVar[int]
    csv_column_list: str
    flags: int
    def __init__(self, csv_column_list: _Optional[str] = ..., flags: _Optional[int] = ...) -> None: ...

class ExportCsvEntityReportResponse(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: int
    def __init__(self, result: _Optional[int] = ...) -> None: ...

class ExportJsonEntityReportRequest(_message.Message):
    __slots__ = ("flags",)
    FLAGS_FIELD_NUMBER: _ClassVar[int]
    flags: int
    def __init__(self, flags: _Optional[int] = ...) -> None: ...

class ExportJsonEntityReportResponse(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: int
    def __init__(self, result: _Optional[int] = ...) -> None: ...

class FetchNextRequest(_message.Message):
    __slots__ = ("export_handle",)
    EXPORT_HANDLE_FIELD_NUMBER: _ClassVar[int]
    export_handle: int
    def __init__(self, export_handle: _Optional[int] = ...) -> None: ...

class FetchNextResponse(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: str
    def __init__(self, result: _Optional[str] = ...) -> None: ...

class FindInterestingEntitiesByEntityIdRequest(_message.Message):
    __slots__ = ("entity_id", "flags")
    ENTITY_ID_FIELD_NUMBER: _ClassVar[int]
    FLAGS_FIELD_NUMBER: _ClassVar[int]
    entity_id: int
    flags: int
    def __init__(self, entity_id: _Optional[int] = ..., flags: _Optional[int] = ...) -> None: ...

class FindInterestingEntitiesByEntityIdResponse(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: str
    def __init__(self, result: _Optional[str] = ...) -> None: ...

class FindInterestingEntitiesByRecordIdRequest(_message.Message):
    __slots__ = ("data_source_code", "record_id", "flags")
    DATA_SOURCE_CODE_FIELD_NUMBER: _ClassVar[int]
    RECORD_ID_FIELD_NUMBER: _ClassVar[int]
    FLAGS_FIELD_NUMBER: _ClassVar[int]
    data_source_code: str
    record_id: str
    flags: int
    def __init__(self, data_source_code: _Optional[str] = ..., record_id: _Optional[str] = ..., flags: _Optional[int] = ...) -> None: ...

class FindInterestingEntitiesByRecordIdResponse(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: str
    def __init__(self, result: _Optional[str] = ...) -> None: ...

class FindNetworkByEntityIdRequest(_message.Message):
    __slots__ = ("entity_ids", "max_degrees", "build_out_degrees", "build_out_max_entities", "flags")
    ENTITY_IDS_FIELD_NUMBER: _ClassVar[int]
    MAX_DEGREES_FIELD_NUMBER: _ClassVar[int]
    BUILD_OUT_DEGREES_FIELD_NUMBER: _ClassVar[int]
    BUILD_OUT_MAX_ENTITIES_FIELD_NUMBER: _ClassVar[int]
    FLAGS_FIELD_NUMBER: _ClassVar[int]
    entity_ids: str
    max_degrees: int
    build_out_degrees: int
    build_out_max_entities: int
    flags: int
    def __init__(self, entity_ids: _Optional[str] = ..., max_degrees: _Optional[int] = ..., build_out_degrees: _Optional[int] = ..., build_out_max_entities: _Optional[int] = ..., flags: _Optional[int] = ...) -> None: ...

class FindNetworkByEntityIdResponse(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: str
    def __init__(self, result: _Optional[str] = ...) -> None: ...

class FindNetworkByRecordIdRequest(_message.Message):
    __slots__ = ("record_keys", "max_degrees", "build_out_degrees", "build_out_max_entities", "flags")
    RECORD_KEYS_FIELD_NUMBER: _ClassVar[int]
    MAX_DEGREES_FIELD_NUMBER: _ClassVar[int]
    BUILD_OUT_DEGREES_FIELD_NUMBER: _ClassVar[int]
    BUILD_OUT_MAX_ENTITIES_FIELD_NUMBER: _ClassVar[int]
    FLAGS_FIELD_NUMBER: _ClassVar[int]
    record_keys: str
    max_degrees: int
    build_out_degrees: int
    build_out_max_entities: int
    flags: int
    def __init__(self, record_keys: _Optional[str] = ..., max_degrees: _Optional[int] = ..., build_out_degrees: _Optional[int] = ..., build_out_max_entities: _Optional[int] = ..., flags: _Optional[int] = ...) -> None: ...

class FindNetworkByRecordIdResponse(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: str
    def __init__(self, result: _Optional[str] = ...) -> None: ...

class FindPathByEntityIdRequest(_message.Message):
    __slots__ = ("start_entity_id", "end_entity_id", "max_degrees", "avoid_entity_ids", "required_data_sources", "flags")
    START_ENTITY_ID_FIELD_NUMBER: _ClassVar[int]
    END_ENTITY_ID_FIELD_NUMBER: _ClassVar[int]
    MAX_DEGREES_FIELD_NUMBER: _ClassVar[int]
    AVOID_ENTITY_IDS_FIELD_NUMBER: _ClassVar[int]
    REQUIRED_DATA_SOURCES_FIELD_NUMBER: _ClassVar[int]
    FLAGS_FIELD_NUMBER: _ClassVar[int]
    start_entity_id: int
    end_entity_id: int
    max_degrees: int
    avoid_entity_ids: str
    required_data_sources: str
    flags: int
    def __init__(self, start_entity_id: _Optional[int] = ..., end_entity_id: _Optional[int] = ..., max_degrees: _Optional[int] = ..., avoid_entity_ids: _Optional[str] = ..., required_data_sources: _Optional[str] = ..., flags: _Optional[int] = ...) -> None: ...

class FindPathByEntityIdResponse(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: str
    def __init__(self, result: _Optional[str] = ...) -> None: ...

class FindPathByRecordIdRequest(_message.Message):
    __slots__ = ("start_data_source_code", "start_record_id", "end_data_source_code", "end_record_id", "max_degrees", "avoid_record_keys", "required_data_sources", "flags")
    START_DATA_SOURCE_CODE_FIELD_NUMBER: _ClassVar[int]
    START_RECORD_ID_FIELD_NUMBER: _ClassVar[int]
    END_DATA_SOURCE_CODE_FIELD_NUMBER: _ClassVar[int]
    END_RECORD_ID_FIELD_NUMBER: _ClassVar[int]
    MAX_DEGREES_FIELD_NUMBER: _ClassVar[int]
    AVOID_RECORD_KEYS_FIELD_NUMBER: _ClassVar[int]
    REQUIRED_DATA_SOURCES_FIELD_NUMBER: _ClassVar[int]
    FLAGS_FIELD_NUMBER: _ClassVar[int]
    start_data_source_code: str
    start_record_id: str
    end_data_source_code: str
    end_record_id: str
    max_degrees: int
    avoid_record_keys: str
    required_data_sources: str
    flags: int
    def __init__(self, start_data_source_code: _Optional[str] = ..., start_record_id: _Optional[str] = ..., end_data_source_code: _Optional[str] = ..., end_record_id: _Optional[str] = ..., max_degrees: _Optional[int] = ..., avoid_record_keys: _Optional[str] = ..., required_data_sources: _Optional[str] = ..., flags: _Optional[int] = ...) -> None: ...

class FindPathByRecordIdResponse(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: str
    def __init__(self, result: _Optional[str] = ...) -> None: ...

class GetActiveConfigIdRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetActiveConfigIdResponse(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: int
    def __init__(self, result: _Optional[int] = ...) -> None: ...

class GetEntityByEntityIdRequest(_message.Message):
    __slots__ = ("entity_id", "flags")
    ENTITY_ID_FIELD_NUMBER: _ClassVar[int]
    FLAGS_FIELD_NUMBER: _ClassVar[int]
    entity_id: int
    flags: int
    def __init__(self, entity_id: _Optional[int] = ..., flags: _Optional[int] = ...) -> None: ...

class GetEntityByEntityIdResponse(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: str
    def __init__(self, result: _Optional[str] = ...) -> None: ...

class GetEntityByRecordIdRequest(_message.Message):
    __slots__ = ("data_source_code", "record_id", "flags")
    DATA_SOURCE_CODE_FIELD_NUMBER: _ClassVar[int]
    RECORD_ID_FIELD_NUMBER: _ClassVar[int]
    FLAGS_FIELD_NUMBER: _ClassVar[int]
    data_source_code: str
    record_id: str
    flags: int
    def __init__(self, data_source_code: _Optional[str] = ..., record_id: _Optional[str] = ..., flags: _Optional[int] = ...) -> None: ...

class GetEntityByRecordIdResponse(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: str
    def __init__(self, result: _Optional[str] = ...) -> None: ...

class GetRecordPreviewRequest(_message.Message):
    __slots__ = ("record_definition", "flags")
    RECORD_DEFINITION_FIELD_NUMBER: _ClassVar[int]
    FLAGS_FIELD_NUMBER: _ClassVar[int]
    record_definition: str
    flags: int
    def __init__(self, record_definition: _Optional[str] = ..., flags: _Optional[int] = ...) -> None: ...

class GetRecordPreviewResponse(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: str
    def __init__(self, result: _Optional[str] = ...) -> None: ...

class GetRecordRequest(_message.Message):
    __slots__ = ("data_source_code", "record_id", "flags")
    DATA_SOURCE_CODE_FIELD_NUMBER: _ClassVar[int]
    RECORD_ID_FIELD_NUMBER: _ClassVar[int]
    FLAGS_FIELD_NUMBER: _ClassVar[int]
    data_source_code: str
    record_id: str
    flags: int
    def __init__(self, data_source_code: _Optional[str] = ..., record_id: _Optional[str] = ..., flags: _Optional[int] = ...) -> None: ...

class GetRecordResponse(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: str
    def __init__(self, result: _Optional[str] = ...) -> None: ...

class GetRedoRecordRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetRedoRecordResponse(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: str
    def __init__(self, result: _Optional[str] = ...) -> None: ...

class GetStatsRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetStatsResponse(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: str
    def __init__(self, result: _Optional[str] = ...) -> None: ...

class GetVirtualEntityByRecordIdRequest(_message.Message):
    __slots__ = ("record_keys", "flags")
    RECORD_KEYS_FIELD_NUMBER: _ClassVar[int]
    FLAGS_FIELD_NUMBER: _ClassVar[int]
    record_keys: str
    flags: int
    def __init__(self, record_keys: _Optional[str] = ..., flags: _Optional[int] = ...) -> None: ...

class GetVirtualEntityByRecordIdResponse(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: str
    def __init__(self, result: _Optional[str] = ...) -> None: ...

class HowEntityByEntityIdRequest(_message.Message):
    __slots__ = ("entity_id", "flags")
    ENTITY_ID_FIELD_NUMBER: _ClassVar[int]
    FLAGS_FIELD_NUMBER: _ClassVar[int]
    entity_id: int
    flags: int
    def __init__(self, entity_id: _Optional[int] = ..., flags: _Optional[int] = ...) -> None: ...

class HowEntityByEntityIdResponse(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: str
    def __init__(self, result: _Optional[str] = ...) -> None: ...

class PrimeEngineRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class PrimeEngineResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ProcessRedoRecordRequest(_message.Message):
    __slots__ = ("redo_record", "flags")
    REDO_RECORD_FIELD_NUMBER: _ClassVar[int]
    FLAGS_FIELD_NUMBER: _ClassVar[int]
    redo_record: str
    flags: int
    def __init__(self, redo_record: _Optional[str] = ..., flags: _Optional[int] = ...) -> None: ...

class ProcessRedoRecordResponse(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: str
    def __init__(self, result: _Optional[str] = ...) -> None: ...

class ReevaluateEntityRequest(_message.Message):
    __slots__ = ("entity_id", "flags")
    ENTITY_ID_FIELD_NUMBER: _ClassVar[int]
    FLAGS_FIELD_NUMBER: _ClassVar[int]
    entity_id: int
    flags: int
    def __init__(self, entity_id: _Optional[int] = ..., flags: _Optional[int] = ...) -> None: ...

class ReevaluateEntityResponse(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: str
    def __init__(self, result: _Optional[str] = ...) -> None: ...

class ReevaluateRecordRequest(_message.Message):
    __slots__ = ("data_source_code", "record_id", "flags")
    DATA_SOURCE_CODE_FIELD_NUMBER: _ClassVar[int]
    RECORD_ID_FIELD_NUMBER: _ClassVar[int]
    FLAGS_FIELD_NUMBER: _ClassVar[int]
    data_source_code: str
    record_id: str
    flags: int
    def __init__(self, data_source_code: _Optional[str] = ..., record_id: _Optional[str] = ..., flags: _Optional[int] = ...) -> None: ...

class ReevaluateRecordResponse(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: str
    def __init__(self, result: _Optional[str] = ...) -> None: ...

class ReinitializeRequest(_message.Message):
    __slots__ = ("config_id",)
    CONFIG_ID_FIELD_NUMBER: _ClassVar[int]
    config_id: int
    def __init__(self, config_id: _Optional[int] = ...) -> None: ...

class ReinitializeResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class SearchByAttributesRequest(_message.Message):
    __slots__ = ("attributes", "search_profile", "flags")
    ATTRIBUTES_FIELD_NUMBER: _ClassVar[int]
    SEARCH_PROFILE_FIELD_NUMBER: _ClassVar[int]
    FLAGS_FIELD_NUMBER: _ClassVar[int]
    attributes: str
    search_profile: str
    flags: int
    def __init__(self, attributes: _Optional[str] = ..., search_profile: _Optional[str] = ..., flags: _Optional[int] = ...) -> None: ...

class SearchByAttributesResponse(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: str
    def __init__(self, result: _Optional[str] = ...) -> None: ...

class StreamExportCsvEntityReportRequest(_message.Message):
    __slots__ = ("csv_column_list", "flags")
    CSV_COLUMN_LIST_FIELD_NUMBER: _ClassVar[int]
    FLAGS_FIELD_NUMBER: _ClassVar[int]
    csv_column_list: str
    flags: int
    def __init__(self, csv_column_list: _Optional[str] = ..., flags: _Optional[int] = ...) -> None: ...

class StreamExportCsvEntityReportResponse(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: str
    def __init__(self, result: _Optional[str] = ...) -> None: ...

class StreamExportJsonEntityReportRequest(_message.Message):
    __slots__ = ("flags",)
    FLAGS_FIELD_NUMBER: _ClassVar[int]
    flags: int
    def __init__(self, flags: _Optional[int] = ...) -> None: ...

class StreamExportJsonEntityReportResponse(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: str
    def __init__(self, result: _Optional[str] = ...) -> None: ...

class WhyEntitiesRequest(_message.Message):
    __slots__ = ("entity_id_1", "entity_id_2", "flags")
    ENTITY_ID_1_FIELD_NUMBER: _ClassVar[int]
    ENTITY_ID_2_FIELD_NUMBER: _ClassVar[int]
    FLAGS_FIELD_NUMBER: _ClassVar[int]
    entity_id_1: int
    entity_id_2: int
    flags: int
    def __init__(self, entity_id_1: _Optional[int] = ..., entity_id_2: _Optional[int] = ..., flags: _Optional[int] = ...) -> None: ...

class WhyEntitiesResponse(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: str
    def __init__(self, result: _Optional[str] = ...) -> None: ...

class WhyRecordInEntityRequest(_message.Message):
    __slots__ = ("data_source_code", "record_id", "flags")
    DATA_SOURCE_CODE_FIELD_NUMBER: _ClassVar[int]
    RECORD_ID_FIELD_NUMBER: _ClassVar[int]
    FLAGS_FIELD_NUMBER: _ClassVar[int]
    data_source_code: str
    record_id: str
    flags: int
    def __init__(self, data_source_code: _Optional[str] = ..., record_id: _Optional[str] = ..., flags: _Optional[int] = ...) -> None: ...

class WhyRecordInEntityResponse(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: str
    def __init__(self, result: _Optional[str] = ...) -> None: ...

class WhyRecordsRequest(_message.Message):
    __slots__ = ("data_source_code_1", "record_id_1", "data_source_code_2", "record_id_2", "flags")
    DATA_SOURCE_CODE_1_FIELD_NUMBER: _ClassVar[int]
    RECORD_ID_1_FIELD_NUMBER: _ClassVar[int]
    DATA_SOURCE_CODE_2_FIELD_NUMBER: _ClassVar[int]
    RECORD_ID_2_FIELD_NUMBER: _ClassVar[int]
    FLAGS_FIELD_NUMBER: _ClassVar[int]
    data_source_code_1: str
    record_id_1: str
    data_source_code_2: str
    record_id_2: str
    flags: int
    def __init__(self, data_source_code_1: _Optional[str] = ..., record_id_1: _Optional[str] = ..., data_source_code_2: _Optional[str] = ..., record_id_2: _Optional[str] = ..., flags: _Optional[int] = ...) -> None: ...

class WhyRecordsResponse(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: str
    def __init__(self, result: _Optional[str] = ...) -> None: ...

class WhySearchRequest(_message.Message):
    __slots__ = ("attributes", "entity_id", "search_profile", "flags")
    ATTRIBUTES_FIELD_NUMBER: _ClassVar[int]
    ENTITY_ID_FIELD_NUMBER: _ClassVar[int]
    SEARCH_PROFILE_FIELD_NUMBER: _ClassVar[int]
    FLAGS_FIELD_NUMBER: _ClassVar[int]
    attributes: str
    entity_id: int
    search_profile: str
    flags: int
    def __init__(self, attributes: _Optional[str] = ..., entity_id: _Optional[int] = ..., search_profile: _Optional[str] = ..., flags: _Optional[int] = ...) -> None: ...

class WhySearchResponse(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: str
    def __init__(self, result: _Optional[str] = ...) -> None: ...
