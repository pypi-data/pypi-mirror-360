from yeying.api.common import message_pb2 as _message_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
from yeying.api.apps.zuoyepigai import meta_pb2 as _meta_pb2
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

class DetailWarehouseRequest(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: DetailWarehouseRequestBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[DetailWarehouseRequestBody, _Mapping]] = ...,
    ) -> None: ...

class DetailWarehouseRequestBody(_message.Message):
    __slots__ = ("uid",)
    UID_FIELD_NUMBER: _ClassVar[int]
    uid: str
    def __init__(self, uid: _Optional[str] = ...) -> None: ...

class DetailWarehouseResponse(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: DetailWarehouseResponseBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[DetailWarehouseResponseBody, _Mapping]] = ...,
    ) -> None: ...

class DetailWarehouseResponseBody(_message.Message):
    __slots__ = ("status", "meta")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    META_FIELD_NUMBER: _ClassVar[int]
    status: _message_pb2.ResponseStatus
    meta: _meta_pb2.WarehouseMetadata
    def __init__(
        self,
        status: _Optional[_Union[_message_pb2.ResponseStatus, _Mapping]] = ...,
        meta: _Optional[_Union[_meta_pb2.WarehouseMetadata, _Mapping]] = ...,
    ) -> None: ...

class AddWarehouseRequest(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: AddWarehouseRequestBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[AddWarehouseRequestBody, _Mapping]] = ...,
    ) -> None: ...

class AddWarehouseRequestBody(_message.Message):
    __slots__ = ("meta",)
    META_FIELD_NUMBER: _ClassVar[int]
    meta: _meta_pb2.WarehouseMetadata
    def __init__(self, meta: _Optional[_Union[_meta_pb2.WarehouseMetadata, _Mapping]] = ...) -> None: ...

class AddWarehouseResponse(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: AddWarehouseResponseBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[AddWarehouseResponseBody, _Mapping]] = ...,
    ) -> None: ...

class AddWarehouseResponseBody(_message.Message):
    __slots__ = ("status", "meta")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    META_FIELD_NUMBER: _ClassVar[int]
    status: _message_pb2.ResponseStatus
    meta: _meta_pb2.WarehouseMetadata
    def __init__(
        self,
        status: _Optional[_Union[_message_pb2.ResponseStatus, _Mapping]] = ...,
        meta: _Optional[_Union[_meta_pb2.WarehouseMetadata, _Mapping]] = ...,
    ) -> None: ...

class ListWarehouseRequest(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: ListWarehouseRequestBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[ListWarehouseRequestBody, _Mapping]] = ...,
    ) -> None: ...

class ListWarehouseRequestBody(_message.Message):
    __slots__ = ("did", "taskUid", "pageIndex", "pageSize")
    DID_FIELD_NUMBER: _ClassVar[int]
    TASKUID_FIELD_NUMBER: _ClassVar[int]
    PAGEINDEX_FIELD_NUMBER: _ClassVar[int]
    PAGESIZE_FIELD_NUMBER: _ClassVar[int]
    did: str
    taskUid: str
    pageIndex: _wrappers_pb2.Int32Value
    pageSize: _wrappers_pb2.Int32Value
    def __init__(
        self,
        did: _Optional[str] = ...,
        taskUid: _Optional[str] = ...,
        pageIndex: _Optional[_Union[_wrappers_pb2.Int32Value, _Mapping]] = ...,
        pageSize: _Optional[_Union[_wrappers_pb2.Int32Value, _Mapping]] = ...,
    ) -> None: ...

class ListWarehouseResponse(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: ListWarehouseResponseBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[ListWarehouseResponseBody, _Mapping]] = ...,
    ) -> None: ...

class ListWarehouseResponseBody(_message.Message):
    __slots__ = ("status", "list", "total")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    LIST_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    status: _message_pb2.ResponseStatus
    list: _containers.RepeatedCompositeFieldContainer[_meta_pb2.WarehouseMetadata]
    total: int
    def __init__(
        self,
        status: _Optional[_Union[_message_pb2.ResponseStatus, _Mapping]] = ...,
        list: _Optional[_Iterable[_Union[_meta_pb2.WarehouseMetadata, _Mapping]]] = ...,
        total: _Optional[int] = ...,
    ) -> None: ...
