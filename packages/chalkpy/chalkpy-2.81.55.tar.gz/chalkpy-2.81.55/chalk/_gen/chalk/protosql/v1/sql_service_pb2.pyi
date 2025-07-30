from chalk._gen.chalk.auth.v1 import permissions_pb2 as _permissions_pb2
from chalk._gen.chalk.common.v1 import chalk_error_pb2 as _chalk_error_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import (
    ClassVar as _ClassVar,
    Iterable as _Iterable,
    Mapping as _Mapping,
    Optional as _Optional,
    Union as _Union,
)

DESCRIPTOR: _descriptor.FileDescriptor

class ExecuteSqlQueryRequest(_message.Message):
    __slots__ = ("query",)
    QUERY_FIELD_NUMBER: _ClassVar[int]
    query: str
    def __init__(self, query: _Optional[str] = ...) -> None: ...

class ExecuteSqlQueryResponse(_message.Message):
    __slots__ = ("query_id", "parquet", "errors")
    QUERY_ID_FIELD_NUMBER: _ClassVar[int]
    PARQUET_FIELD_NUMBER: _ClassVar[int]
    ERRORS_FIELD_NUMBER: _ClassVar[int]
    query_id: str
    parquet: bytes
    errors: _containers.RepeatedCompositeFieldContainer[_chalk_error_pb2.ChalkError]
    def __init__(
        self,
        query_id: _Optional[str] = ...,
        parquet: _Optional[bytes] = ...,
        errors: _Optional[_Iterable[_Union[_chalk_error_pb2.ChalkError, _Mapping]]] = ...,
    ) -> None: ...

class PlanSqlQueryRequest(_message.Message):
    __slots__ = ("query",)
    QUERY_FIELD_NUMBER: _ClassVar[int]
    query: str
    def __init__(self, query: _Optional[str] = ...) -> None: ...

class PlanSqlQueryResponse(_message.Message):
    __slots__ = ("logical_plan",)
    LOGICAL_PLAN_FIELD_NUMBER: _ClassVar[int]
    logical_plan: str
    def __init__(self, logical_plan: _Optional[str] = ...) -> None: ...
