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

class MistakesListRequest(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: MistakesListRequestBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[MistakesListRequestBody, _Mapping]] = ...,
    ) -> None: ...

class MistakesListRequestBody(_message.Message):
    __slots__ = ("did",)
    DID_FIELD_NUMBER: _ClassVar[int]
    did: str
    def __init__(self, did: _Optional[str] = ...) -> None: ...

class MistakesListResponse(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: MistakesListResponseBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[MistakesListResponseBody, _Mapping]] = ...,
    ) -> None: ...

class MistakesListResponseBody(_message.Message):
    __slots__ = ("status", "list")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    LIST_FIELD_NUMBER: _ClassVar[int]
    status: _message_pb2.ResponseStatus
    list: _containers.RepeatedCompositeFieldContainer[_meta_pb2.MistakesMetadata]
    def __init__(
        self,
        status: _Optional[_Union[_message_pb2.ResponseStatus, _Mapping]] = ...,
        list: _Optional[_Iterable[_Union[_meta_pb2.MistakesMetadata, _Mapping]]] = ...,
    ) -> None: ...

class MistakesDetailRequest(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: MistakesDetailRequestBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[MistakesDetailRequestBody, _Mapping]] = ...,
    ) -> None: ...

class MistakesDetailRequestBody(_message.Message):
    __slots__ = ("uid",)
    UID_FIELD_NUMBER: _ClassVar[int]
    uid: str
    def __init__(self, uid: _Optional[str] = ...) -> None: ...

class MistakesDetailResponse(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: MistakesDetailResponseBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[MistakesDetailResponseBody, _Mapping]] = ...,
    ) -> None: ...

class MistakesDetailResponseBody(_message.Message):
    __slots__ = ("status", "meta")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    META_FIELD_NUMBER: _ClassVar[int]
    status: _message_pb2.ResponseStatus
    meta: _meta_pb2.MistakesMetadata
    def __init__(
        self,
        status: _Optional[_Union[_message_pb2.ResponseStatus, _Mapping]] = ...,
        meta: _Optional[_Union[_meta_pb2.MistakesMetadata, _Mapping]] = ...,
    ) -> None: ...

class MistakesAnalysisRequest(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: MistakesAnalysisRequestBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[MistakesAnalysisRequestBody, _Mapping]] = ...,
    ) -> None: ...

class MistakesAnalysisRequestBody(_message.Message):
    __slots__ = ("qa",)
    QA_FIELD_NUMBER: _ClassVar[int]
    qa: str
    def __init__(self, qa: _Optional[str] = ...) -> None: ...

class MistakesAnalysisResponse(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: MistakesAnalysisResponseBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[MistakesAnalysisResponseBody, _Mapping]] = ...,
    ) -> None: ...

class MistakesAnalysisResponseBody(_message.Message):
    __slots__ = ("status",)
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: _message_pb2.ResponseStatus
    def __init__(self, status: _Optional[_Union[_message_pb2.ResponseStatus, _Mapping]] = ...) -> None: ...

class MakeCorrectionRequest(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: MakeCorrectionRequestBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[MakeCorrectionRequestBody, _Mapping]] = ...,
    ) -> None: ...

class MakeCorrectionRequestBody(_message.Message):
    __slots__ = ("qa",)
    QA_FIELD_NUMBER: _ClassVar[int]
    qa: str
    def __init__(self, qa: _Optional[str] = ...) -> None: ...

class MakeCorrectionResponse(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: MakeCorrectionResponseBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[MakeCorrectionResponseBody, _Mapping]] = ...,
    ) -> None: ...

class MakeCorrectionResponseBody(_message.Message):
    __slots__ = ("status",)
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: _message_pb2.ResponseStatus
    def __init__(self, status: _Optional[_Union[_message_pb2.ResponseStatus, _Mapping]] = ...) -> None: ...

class MistakesPrintRequest(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: MistakesPrintRequestBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[MistakesPrintRequestBody, _Mapping]] = ...,
    ) -> None: ...

class MistakesPrintRequestBody(_message.Message):
    __slots__ = ("qa",)
    QA_FIELD_NUMBER: _ClassVar[int]
    qa: str
    def __init__(self, qa: _Optional[str] = ...) -> None: ...

class MistakesPrintResponse(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: MistakesPrintResponseBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[MistakesPrintResponseBody, _Mapping]] = ...,
    ) -> None: ...

class MistakesPrintResponseBody(_message.Message):
    __slots__ = ("status",)
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: _message_pb2.ResponseStatus
    def __init__(self, status: _Optional[_Union[_message_pb2.ResponseStatus, _Mapping]] = ...) -> None: ...

class MistakesSubmitRequest(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: MistakesSubmitRequestBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[MistakesSubmitRequestBody, _Mapping]] = ...,
    ) -> None: ...

class MistakesSubmitRequestBody(_message.Message):
    __slots__ = ("qa",)
    QA_FIELD_NUMBER: _ClassVar[int]
    qa: str
    def __init__(self, qa: _Optional[str] = ...) -> None: ...

class MistakesSubmitResponse(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: MistakesSubmitResponseBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[MistakesSubmitResponseBody, _Mapping]] = ...,
    ) -> None: ...

class MistakesSubmitResponseBody(_message.Message):
    __slots__ = ("status",)
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: _message_pb2.ResponseStatus
    def __init__(self, status: _Optional[_Union[_message_pb2.ResponseStatus, _Mapping]] = ...) -> None: ...
