from yeying.api.common import message_pb2 as _message_pb2
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

class AddTaskTagRequest(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: AddTaskTagRequestBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[AddTaskTagRequestBody, _Mapping]] = ...,
    ) -> None: ...

class AddTaskTagRequestBody(_message.Message):
    __slots__ = ("meta",)
    META_FIELD_NUMBER: _ClassVar[int]
    meta: _meta_pb2.TaskTagMetadata
    def __init__(self, meta: _Optional[_Union[_meta_pb2.TaskTagMetadata, _Mapping]] = ...) -> None: ...

class AddTaskTagResponse(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: AddTaskTagResponseBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[AddTaskTagResponseBody, _Mapping]] = ...,
    ) -> None: ...

class AddTaskTagResponseBody(_message.Message):
    __slots__ = ("status", "meta")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    META_FIELD_NUMBER: _ClassVar[int]
    status: _message_pb2.ResponseStatus
    meta: _meta_pb2.TaskTagMetadata
    def __init__(
        self,
        status: _Optional[_Union[_message_pb2.ResponseStatus, _Mapping]] = ...,
        meta: _Optional[_Union[_meta_pb2.TaskTagMetadata, _Mapping]] = ...,
    ) -> None: ...

class DetailTaskTagRequest(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: DetailTaskTagRequestBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[DetailTaskTagRequestBody, _Mapping]] = ...,
    ) -> None: ...

class DetailTaskTagRequestBody(_message.Message):
    __slots__ = ("uid",)
    UID_FIELD_NUMBER: _ClassVar[int]
    uid: str
    def __init__(self, uid: _Optional[str] = ...) -> None: ...

class DetailTaskTagResponse(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: DetailTaskTagResponseBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[DetailTaskTagResponseBody, _Mapping]] = ...,
    ) -> None: ...

class DetailTaskTagResponseBody(_message.Message):
    __slots__ = ("status", "meta")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    META_FIELD_NUMBER: _ClassVar[int]
    status: _message_pb2.ResponseStatus
    meta: _meta_pb2.TaskTagMetadata
    def __init__(
        self,
        status: _Optional[_Union[_message_pb2.ResponseStatus, _Mapping]] = ...,
        meta: _Optional[_Union[_meta_pb2.TaskTagMetadata, _Mapping]] = ...,
    ) -> None: ...

class ListTaskTagRequest(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: ListTaskTagRequestBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[ListTaskTagRequestBody, _Mapping]] = ...,
    ) -> None: ...

class ListTaskTagRequestBody(_message.Message):
    __slots__ = ("did",)
    DID_FIELD_NUMBER: _ClassVar[int]
    did: str
    def __init__(self, did: _Optional[str] = ...) -> None: ...

class ListTaskTagResponse(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: ListTaskTagResponseBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[ListTaskTagResponseBody, _Mapping]] = ...,
    ) -> None: ...

class ListTaskTagResponseBody(_message.Message):
    __slots__ = ("status", "list")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    LIST_FIELD_NUMBER: _ClassVar[int]
    status: _message_pb2.ResponseStatus
    list: _containers.RepeatedCompositeFieldContainer[_meta_pb2.TaskTagMetadata]
    def __init__(
        self,
        status: _Optional[_Union[_message_pb2.ResponseStatus, _Mapping]] = ...,
        list: _Optional[_Iterable[_Union[_meta_pb2.TaskTagMetadata, _Mapping]]] = ...,
    ) -> None: ...

class UpdateTaskTagRequest(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: UpdateTaskTagRequestBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[UpdateTaskTagRequestBody, _Mapping]] = ...,
    ) -> None: ...

class UpdateTaskTagRequestBody(_message.Message):
    __slots__ = ("meta",)
    META_FIELD_NUMBER: _ClassVar[int]
    meta: _meta_pb2.TaskTagMetadata
    def __init__(self, meta: _Optional[_Union[_meta_pb2.TaskTagMetadata, _Mapping]] = ...) -> None: ...

class UpdateTaskTagResponse(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: UpdateTaskTagResponseBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[UpdateTaskTagResponseBody, _Mapping]] = ...,
    ) -> None: ...

class UpdateTaskTagResponseBody(_message.Message):
    __slots__ = ("status", "meta")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    META_FIELD_NUMBER: _ClassVar[int]
    status: _message_pb2.ResponseStatus
    meta: _meta_pb2.TaskTagMetadata
    def __init__(
        self,
        status: _Optional[_Union[_message_pb2.ResponseStatus, _Mapping]] = ...,
        meta: _Optional[_Union[_meta_pb2.TaskTagMetadata, _Mapping]] = ...,
    ) -> None: ...

class DeleteTaskTagRequest(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: DeleteTaskTagRequestBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[DeleteTaskTagRequestBody, _Mapping]] = ...,
    ) -> None: ...

class DeleteTaskTagRequestBody(_message.Message):
    __slots__ = ("uid",)
    UID_FIELD_NUMBER: _ClassVar[int]
    uid: str
    def __init__(self, uid: _Optional[str] = ...) -> None: ...

class DeleteTaskTagResponse(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: DeleteTaskTagResponseBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[DeleteTaskTagResponseBody, _Mapping]] = ...,
    ) -> None: ...

class DeleteTaskTagResponseBody(_message.Message):
    __slots__ = ("status", "meta")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    META_FIELD_NUMBER: _ClassVar[int]
    status: _message_pb2.ResponseStatus
    meta: _meta_pb2.TaskTagMetadata
    def __init__(
        self,
        status: _Optional[_Union[_message_pb2.ResponseStatus, _Mapping]] = ...,
        meta: _Optional[_Union[_meta_pb2.TaskTagMetadata, _Mapping]] = ...,
    ) -> None: ...
