from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class QueryType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    QUERY_TYPE_UNKNOWN: _ClassVar[QueryType]
    QUERY_TYPE_INTERVAL: _ClassVar[QueryType]
    QUERY_TYPE_SNAPSHOT: _ClassVar[QueryType]
    QUERY_TYPE_TIME: _ClassVar[QueryType]
    QUERY_TYPE_TIME_SNAPSHOT: _ClassVar[QueryType]
    QUERY_TYPE_TIME_TRANSPOSE: _ClassVar[QueryType]
    QUERY_TYPE_TIME_SNAPSHOT_TRANSPOSE: _ClassVar[QueryType]
    QUERY_TYPE_INTERVAL_RAW: _ClassVar[QueryType]
    QUERY_TYPE_TIME_SNAPSHOT_RAW: _ClassVar[QueryType]

class ServiceType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SERVICE_TYPE_UNKNOWN: _ClassVar[ServiceType]
    SERVICE_TYPE_INTERVAL: _ClassVar[ServiceType]
    SERVICE_TYPE_SNAPSHOT: _ClassVar[ServiceType]
    SERVICE_TYPE_TIME: _ClassVar[ServiceType]
    SERVICE_TYPE_TIME_SNAP: _ClassVar[ServiceType]
QUERY_TYPE_UNKNOWN: QueryType
QUERY_TYPE_INTERVAL: QueryType
QUERY_TYPE_SNAPSHOT: QueryType
QUERY_TYPE_TIME: QueryType
QUERY_TYPE_TIME_SNAPSHOT: QueryType
QUERY_TYPE_TIME_TRANSPOSE: QueryType
QUERY_TYPE_TIME_SNAPSHOT_TRANSPOSE: QueryType
QUERY_TYPE_INTERVAL_RAW: QueryType
QUERY_TYPE_TIME_SNAPSHOT_RAW: QueryType
SERVICE_TYPE_UNKNOWN: ServiceType
SERVICE_TYPE_INTERVAL: ServiceType
SERVICE_TYPE_SNAPSHOT: ServiceType
SERVICE_TYPE_TIME: ServiceType
SERVICE_TYPE_TIME_SNAP: ServiceType

class RequestParam(_message.Message):
    __slots__ = ("name", "values")
    NAME_FIELD_NUMBER: _ClassVar[int]
    VALUES_FIELD_NUMBER: _ClassVar[int]
    name: str
    values: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, name: _Optional[str] = ..., values: _Optional[_Iterable[str]] = ...) -> None: ...

class GetTableDataRequest(_message.Message):
    __slots__ = ("name", "query_type", "ids", "fields", "since", "until", "label_start", "label_end", "params")
    NAME_FIELD_NUMBER: _ClassVar[int]
    QUERY_TYPE_FIELD_NUMBER: _ClassVar[int]
    IDS_FIELD_NUMBER: _ClassVar[int]
    FIELDS_FIELD_NUMBER: _ClassVar[int]
    SINCE_FIELD_NUMBER: _ClassVar[int]
    UNTIL_FIELD_NUMBER: _ClassVar[int]
    LABEL_START_FIELD_NUMBER: _ClassVar[int]
    LABEL_END_FIELD_NUMBER: _ClassVar[int]
    PARAMS_FIELD_NUMBER: _ClassVar[int]
    name: str
    query_type: QueryType
    ids: _containers.RepeatedScalarFieldContainer[str]
    fields: _containers.RepeatedScalarFieldContainer[str]
    since: int
    until: int
    label_start: int
    label_end: int
    params: _containers.RepeatedCompositeFieldContainer[RequestParam]
    def __init__(self, name: _Optional[str] = ..., query_type: _Optional[_Union[QueryType, str]] = ..., ids: _Optional[_Iterable[str]] = ..., fields: _Optional[_Iterable[str]] = ..., since: _Optional[int] = ..., until: _Optional[int] = ..., label_start: _Optional[int] = ..., label_end: _Optional[int] = ..., params: _Optional[_Iterable[_Union[RequestParam, _Mapping]]] = ...) -> None: ...

class GetTableDataResponseChunk(_message.Message):
    __slots__ = ("service_type", "data", "is_date_series")
    SERVICE_TYPE_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    IS_DATE_SERIES_FIELD_NUMBER: _ClassVar[int]
    service_type: ServiceType
    data: bytes
    is_date_series: bool
    def __init__(self, service_type: _Optional[_Union[ServiceType, str]] = ..., data: _Optional[bytes] = ..., is_date_series: bool = ...) -> None: ...
