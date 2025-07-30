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

class ArchiveListRequest(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: ArchiveListRequestBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[ArchiveListRequestBody, _Mapping]] = ...,
    ) -> None: ...

class ArchiveListRequestBody(_message.Message):
    __slots__ = ("teacherDid", "name", "pageIndex", "pageSize")
    TEACHERDID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    PAGEINDEX_FIELD_NUMBER: _ClassVar[int]
    PAGESIZE_FIELD_NUMBER: _ClassVar[int]
    teacherDid: str
    name: str
    pageIndex: _wrappers_pb2.Int32Value
    pageSize: _wrappers_pb2.Int32Value
    def __init__(
        self,
        teacherDid: _Optional[str] = ...,
        name: _Optional[str] = ...,
        pageIndex: _Optional[_Union[_wrappers_pb2.Int32Value, _Mapping]] = ...,
        pageSize: _Optional[_Union[_wrappers_pb2.Int32Value, _Mapping]] = ...,
    ) -> None: ...

class ArchiveListResponse(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: ArchiveListResponseBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[ArchiveListResponseBody, _Mapping]] = ...,
    ) -> None: ...

class ArchiveListResponseBody(_message.Message):
    __slots__ = ("status", "list", "total")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    LIST_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    status: _message_pb2.ResponseStatus
    list: _containers.RepeatedCompositeFieldContainer[_meta_pb2.ArchiveMetadata]
    total: int
    def __init__(
        self,
        status: _Optional[_Union[_message_pb2.ResponseStatus, _Mapping]] = ...,
        list: _Optional[_Iterable[_Union[_meta_pb2.ArchiveMetadata, _Mapping]]] = ...,
        total: _Optional[int] = ...,
    ) -> None: ...

class ArchiveDetailRequest(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: ArchiveDetailRequestBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[ArchiveDetailRequestBody, _Mapping]] = ...,
    ) -> None: ...

class ArchiveDetailRequestBody(_message.Message):
    __slots__ = ("uid",)
    UID_FIELD_NUMBER: _ClassVar[int]
    uid: str
    def __init__(self, uid: _Optional[str] = ...) -> None: ...

class ArchiveDetailResponse(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: ArchiveDetailResponseBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[ArchiveDetailResponseBody, _Mapping]] = ...,
    ) -> None: ...

class ArchiveDetailResponseBody(_message.Message):
    __slots__ = ("status", "meta")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    META_FIELD_NUMBER: _ClassVar[int]
    status: _message_pb2.ResponseStatus
    meta: _meta_pb2.ArchiveMetadata
    def __init__(
        self,
        status: _Optional[_Union[_message_pb2.ResponseStatus, _Mapping]] = ...,
        meta: _Optional[_Union[_meta_pb2.ArchiveMetadata, _Mapping]] = ...,
    ) -> None: ...

class ArchiveDetailStudentRequest(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: ArchiveDetailStudentRequestBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[ArchiveDetailStudentRequestBody, _Mapping]] = ...,
    ) -> None: ...

class ArchiveDetailStudentRequestBody(_message.Message):
    __slots__ = ("studentDid",)
    STUDENTDID_FIELD_NUMBER: _ClassVar[int]
    studentDid: str
    def __init__(self, studentDid: _Optional[str] = ...) -> None: ...

class ArchiveDetailStudentResponse(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: ArchiveDetailStudentResponseBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[ArchiveDetailStudentResponseBody, _Mapping]] = ...,
    ) -> None: ...

class ArchiveDetailStudentResponseBody(_message.Message):
    __slots__ = ("status", "meta")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    META_FIELD_NUMBER: _ClassVar[int]
    status: _message_pb2.ResponseStatus
    meta: _meta_pb2.ArchiveMetadata
    def __init__(
        self,
        status: _Optional[_Union[_message_pb2.ResponseStatus, _Mapping]] = ...,
        meta: _Optional[_Union[_meta_pb2.ArchiveMetadata, _Mapping]] = ...,
    ) -> None: ...

class ArchiveAddRequest(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: ArchiveAddRequestBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[ArchiveAddRequestBody, _Mapping]] = ...,
    ) -> None: ...

class ArchiveAddRequestBody(_message.Message):
    __slots__ = ("meta",)
    META_FIELD_NUMBER: _ClassVar[int]
    meta: _meta_pb2.ArchiveMetadata
    def __init__(self, meta: _Optional[_Union[_meta_pb2.ArchiveMetadata, _Mapping]] = ...) -> None: ...

class ArchiveAddResponse(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: ArchiveAddResponseBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[ArchiveAddResponseBody, _Mapping]] = ...,
    ) -> None: ...

class ArchiveAddResponseBody(_message.Message):
    __slots__ = ("status", "meta")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    META_FIELD_NUMBER: _ClassVar[int]
    status: _message_pb2.ResponseStatus
    meta: _meta_pb2.ArchiveMetadata
    def __init__(
        self,
        status: _Optional[_Union[_message_pb2.ResponseStatus, _Mapping]] = ...,
        meta: _Optional[_Union[_meta_pb2.ArchiveMetadata, _Mapping]] = ...,
    ) -> None: ...

class ArchiveDeleteRequest(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: ArchiveDeleteRequestBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[ArchiveDeleteRequestBody, _Mapping]] = ...,
    ) -> None: ...

class ArchiveDeleteRequestBody(_message.Message):
    __slots__ = ("uid",)
    UID_FIELD_NUMBER: _ClassVar[int]
    uid: str
    def __init__(self, uid: _Optional[str] = ...) -> None: ...

class ArchiveDeleteResponse(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: ArchiveDeleteResponseBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[ArchiveDeleteResponseBody, _Mapping]] = ...,
    ) -> None: ...

class ArchiveDeleteResponseBody(_message.Message):
    __slots__ = ("status", "meta")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    META_FIELD_NUMBER: _ClassVar[int]
    status: _message_pb2.ResponseStatus
    meta: _meta_pb2.ArchiveMetadata
    def __init__(
        self,
        status: _Optional[_Union[_message_pb2.ResponseStatus, _Mapping]] = ...,
        meta: _Optional[_Union[_meta_pb2.ArchiveMetadata, _Mapping]] = ...,
    ) -> None: ...

class ArchiveUpdateRequest(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: ArchiveUpdateRequestBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[ArchiveUpdateRequestBody, _Mapping]] = ...,
    ) -> None: ...

class ArchiveUpdateRequestBody(_message.Message):
    __slots__ = ("meta",)
    META_FIELD_NUMBER: _ClassVar[int]
    meta: _meta_pb2.ArchiveMetadata
    def __init__(self, meta: _Optional[_Union[_meta_pb2.ArchiveMetadata, _Mapping]] = ...) -> None: ...

class ArchiveUpdateResponse(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: ArchiveUpdateResponseBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[ArchiveUpdateResponseBody, _Mapping]] = ...,
    ) -> None: ...

class ArchiveUpdateResponseBody(_message.Message):
    __slots__ = ("status", "meta")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    META_FIELD_NUMBER: _ClassVar[int]
    status: _message_pb2.ResponseStatus
    meta: _meta_pb2.ArchiveMetadata
    def __init__(
        self,
        status: _Optional[_Union[_message_pb2.ResponseStatus, _Mapping]] = ...,
        meta: _Optional[_Union[_meta_pb2.ArchiveMetadata, _Mapping]] = ...,
    ) -> None: ...
