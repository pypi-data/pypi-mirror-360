from yeying.api.common import message_pb2 as _message_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
from yeying.api.apps.zuoyepigai import imagecontent_pb2 as _imagecontent_pb2
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

class AddTaskRequest(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: AddTaskRequestBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[AddTaskRequestBody, _Mapping]] = ...,
    ) -> None: ...

class AddTaskRequestBody(_message.Message):
    __slots__ = ("meta",)
    META_FIELD_NUMBER: _ClassVar[int]
    meta: _meta_pb2.TaskMetadata
    def __init__(self, meta: _Optional[_Union[_meta_pb2.TaskMetadata, _Mapping]] = ...) -> None: ...

class AddTaskResponse(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: AddTaskResponseBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[AddTaskResponseBody, _Mapping]] = ...,
    ) -> None: ...

class AddTaskResponseBody(_message.Message):
    __slots__ = ("status", "meta")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    META_FIELD_NUMBER: _ClassVar[int]
    status: _message_pb2.ResponseStatus
    meta: _meta_pb2.TaskMetadata
    def __init__(
        self,
        status: _Optional[_Union[_message_pb2.ResponseStatus, _Mapping]] = ...,
        meta: _Optional[_Union[_meta_pb2.TaskMetadata, _Mapping]] = ...,
    ) -> None: ...

class DetailTaskRequest(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: DetailTaskRequestBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[DetailTaskRequestBody, _Mapping]] = ...,
    ) -> None: ...

class DetailTaskRequestBody(_message.Message):
    __slots__ = ("uid",)
    UID_FIELD_NUMBER: _ClassVar[int]
    uid: str
    def __init__(self, uid: _Optional[str] = ...) -> None: ...

class DetailTaskResponse(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: DetailTaskResponseBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[DetailTaskResponseBody, _Mapping]] = ...,
    ) -> None: ...

class DetailTaskResponseBody(_message.Message):
    __slots__ = ("status", "meta", "studentList")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    META_FIELD_NUMBER: _ClassVar[int]
    STUDENTLIST_FIELD_NUMBER: _ClassVar[int]
    status: _message_pb2.ResponseStatus
    meta: _meta_pb2.TaskMetadata
    studentList: _containers.RepeatedCompositeFieldContainer[_meta_pb2.GroupMetaData]
    def __init__(
        self,
        status: _Optional[_Union[_message_pb2.ResponseStatus, _Mapping]] = ...,
        meta: _Optional[_Union[_meta_pb2.TaskMetadata, _Mapping]] = ...,
        studentList: _Optional[_Iterable[_Union[_meta_pb2.GroupMetaData, _Mapping]]] = ...,
    ) -> None: ...

class ListTaskRequest(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: ListTaskRequestBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[ListTaskRequestBody, _Mapping]] = ...,
    ) -> None: ...

class ListTaskRequestBody(_message.Message):
    __slots__ = ("did", "tagUid", "taskName", "description", "pageIndex", "pageSize", "status", "startTime", "endTime")
    DID_FIELD_NUMBER: _ClassVar[int]
    TAGUID_FIELD_NUMBER: _ClassVar[int]
    TASKNAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    PAGEINDEX_FIELD_NUMBER: _ClassVar[int]
    PAGESIZE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    STARTTIME_FIELD_NUMBER: _ClassVar[int]
    ENDTIME_FIELD_NUMBER: _ClassVar[int]
    did: str
    tagUid: str
    taskName: str
    description: str
    pageIndex: _wrappers_pb2.Int32Value
    pageSize: _wrappers_pb2.Int32Value
    status: int
    startTime: int
    endTime: int
    def __init__(
        self,
        did: _Optional[str] = ...,
        tagUid: _Optional[str] = ...,
        taskName: _Optional[str] = ...,
        description: _Optional[str] = ...,
        pageIndex: _Optional[_Union[_wrappers_pb2.Int32Value, _Mapping]] = ...,
        pageSize: _Optional[_Union[_wrappers_pb2.Int32Value, _Mapping]] = ...,
        status: _Optional[int] = ...,
        startTime: _Optional[int] = ...,
        endTime: _Optional[int] = ...,
    ) -> None: ...

class ListTaskResponse(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: ListTaskResponseBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[ListTaskResponseBody, _Mapping]] = ...,
    ) -> None: ...

class ListTaskResponseBody(_message.Message):
    __slots__ = ("status", "list", "total")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    LIST_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    status: _message_pb2.ResponseStatus
    list: _containers.RepeatedCompositeFieldContainer[_meta_pb2.TaskMetadata]
    total: int
    def __init__(
        self,
        status: _Optional[_Union[_message_pb2.ResponseStatus, _Mapping]] = ...,
        list: _Optional[_Iterable[_Union[_meta_pb2.TaskMetadata, _Mapping]]] = ...,
        total: _Optional[int] = ...,
    ) -> None: ...

class TagCountTaskRequest(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: TagCountTaskRequestBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[TagCountTaskRequestBody, _Mapping]] = ...,
    ) -> None: ...

class TagCountTaskRequestBody(_message.Message):
    __slots__ = ("did",)
    DID_FIELD_NUMBER: _ClassVar[int]
    did: str
    def __init__(self, did: _Optional[str] = ...) -> None: ...

class TagCountTaskResponse(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: TagCountTaskResponseBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[TagCountTaskResponseBody, _Mapping]] = ...,
    ) -> None: ...

class TagCountTaskResponseBody(_message.Message):
    __slots__ = ("status", "meta")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    META_FIELD_NUMBER: _ClassVar[int]
    status: _message_pb2.ResponseStatus
    meta: _containers.RepeatedCompositeFieldContainer[_meta_pb2.TagCountMeta]
    def __init__(
        self,
        status: _Optional[_Union[_message_pb2.ResponseStatus, _Mapping]] = ...,
        meta: _Optional[_Iterable[_Union[_meta_pb2.TagCountMeta, _Mapping]]] = ...,
    ) -> None: ...

class UpdateTaskRequest(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: UpdateTaskRequestBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[UpdateTaskRequestBody, _Mapping]] = ...,
    ) -> None: ...

class UpdateTaskRequestBody(_message.Message):
    __slots__ = ("meta",)
    META_FIELD_NUMBER: _ClassVar[int]
    meta: _meta_pb2.TaskMetadata
    def __init__(self, meta: _Optional[_Union[_meta_pb2.TaskMetadata, _Mapping]] = ...) -> None: ...

class UpdateTaskResponse(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: UpdateTaskResponseBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[UpdateTaskResponseBody, _Mapping]] = ...,
    ) -> None: ...

class UpdateTaskResponseBody(_message.Message):
    __slots__ = ("status", "meta")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    META_FIELD_NUMBER: _ClassVar[int]
    status: _message_pb2.ResponseStatus
    meta: _meta_pb2.TaskMetadata
    def __init__(
        self,
        status: _Optional[_Union[_message_pb2.ResponseStatus, _Mapping]] = ...,
        meta: _Optional[_Union[_meta_pb2.TaskMetadata, _Mapping]] = ...,
    ) -> None: ...

class DeleteTaskRequest(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: DeleteTaskRequestBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[DeleteTaskRequestBody, _Mapping]] = ...,
    ) -> None: ...

class DeleteTaskRequestBody(_message.Message):
    __slots__ = ("uid",)
    UID_FIELD_NUMBER: _ClassVar[int]
    uid: str
    def __init__(self, uid: _Optional[str] = ...) -> None: ...

class DeleteTaskResponse(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: DeleteTaskResponseBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[DeleteTaskResponseBody, _Mapping]] = ...,
    ) -> None: ...

class DeleteTaskResponseBody(_message.Message):
    __slots__ = ("status", "meta")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    META_FIELD_NUMBER: _ClassVar[int]
    status: _message_pb2.ResponseStatus
    meta: _meta_pb2.TaskMetadata
    def __init__(
        self,
        status: _Optional[_Union[_message_pb2.ResponseStatus, _Mapping]] = ...,
        meta: _Optional[_Union[_meta_pb2.TaskMetadata, _Mapping]] = ...,
    ) -> None: ...
