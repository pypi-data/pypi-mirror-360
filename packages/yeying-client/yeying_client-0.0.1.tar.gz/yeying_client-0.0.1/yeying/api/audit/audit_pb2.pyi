from yeying.api.common import message_pb2 as _message_pb2
from yeying.api.common import code_pb2 as _code_pb2
from yeying.api.common import model_pb2 as _model_pb2
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

class AuditStatus(_message.Message):
    __slots__ = ("pending", "canceled", "passed", "reject")
    PENDING_FIELD_NUMBER: _ClassVar[int]
    CANCELED_FIELD_NUMBER: _ClassVar[int]
    PASSED_FIELD_NUMBER: _ClassVar[int]
    REJECT_FIELD_NUMBER: _ClassVar[int]
    pending: PendingStatus
    canceled: CanceledStatus
    passed: PassedStatus
    reject: RejectStatus
    def __init__(
        self,
        pending: _Optional[_Union[PendingStatus, _Mapping]] = ...,
        canceled: _Optional[_Union[CanceledStatus, _Mapping]] = ...,
        passed: _Optional[_Union[PassedStatus, _Mapping]] = ...,
        reject: _Optional[_Union[RejectStatus, _Mapping]] = ...,
    ) -> None: ...

class PendingStatus(_message.Message):
    __slots__ = ("text",)
    TEXT_FIELD_NUMBER: _ClassVar[int]
    text: str
    def __init__(self, text: _Optional[str] = ...) -> None: ...

class CanceledStatus(_message.Message):
    __slots__ = ("text",)
    TEXT_FIELD_NUMBER: _ClassVar[int]
    text: str
    def __init__(self, text: _Optional[str] = ...) -> None: ...

class PassedStatus(_message.Message):
    __slots__ = ("text",)
    TEXT_FIELD_NUMBER: _ClassVar[int]
    text: str
    def __init__(self, text: _Optional[str] = ...) -> None: ...

class RejectStatus(_message.Message):
    __slots__ = ("text",)
    TEXT_FIELD_NUMBER: _ClassVar[int]
    text: str
    def __init__(self, text: _Optional[str] = ...) -> None: ...

class CreateRequest(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: CreateRequestBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[CreateRequestBody, _Mapping]] = ...,
    ) -> None: ...

class CreateRequestBody(_message.Message):
    __slots__ = ("meta",)
    META_FIELD_NUMBER: _ClassVar[int]
    meta: AuditMetadata
    def __init__(self, meta: _Optional[_Union[AuditMetadata, _Mapping]] = ...) -> None: ...

class CreateResponse(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: CreateResponseBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[CreateResponseBody, _Mapping]] = ...,
    ) -> None: ...

class CreateResponseBody(_message.Message):
    __slots__ = ("status", "meta")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    META_FIELD_NUMBER: _ClassVar[int]
    status: _message_pb2.ResponseStatus
    meta: AuditMetadata
    def __init__(
        self,
        status: _Optional[_Union[_message_pb2.ResponseStatus, _Mapping]] = ...,
        meta: _Optional[_Union[AuditMetadata, _Mapping]] = ...,
    ) -> None: ...

class DetailRequest(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: DetailRequestBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[DetailRequestBody, _Mapping]] = ...,
    ) -> None: ...

class DetailRequestBody(_message.Message):
    __slots__ = ("uid",)
    UID_FIELD_NUMBER: _ClassVar[int]
    uid: str
    def __init__(self, uid: _Optional[str] = ...) -> None: ...

class DetailResponse(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: DetailResponseBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[DetailResponseBody, _Mapping]] = ...,
    ) -> None: ...

class DetailResponseBody(_message.Message):
    __slots__ = ("status", "meta")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    META_FIELD_NUMBER: _ClassVar[int]
    status: _message_pb2.ResponseStatus
    meta: AuditMetadata
    def __init__(
        self,
        status: _Optional[_Union[_message_pb2.ResponseStatus, _Mapping]] = ...,
        meta: _Optional[_Union[AuditMetadata, _Mapping]] = ...,
    ) -> None: ...

class CancelRequest(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: CancelRequestBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[CancelRequestBody, _Mapping]] = ...,
    ) -> None: ...

class CancelRequestBody(_message.Message):
    __slots__ = ("uid",)
    UID_FIELD_NUMBER: _ClassVar[int]
    uid: str
    def __init__(self, uid: _Optional[str] = ...) -> None: ...

class CancelResponse(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: CancelResponseBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[CancelResponseBody, _Mapping]] = ...,
    ) -> None: ...

class CancelResponseBody(_message.Message):
    __slots__ = ("status", "meta")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    META_FIELD_NUMBER: _ClassVar[int]
    status: _message_pb2.ResponseStatus
    meta: AuditMetadata
    def __init__(
        self,
        status: _Optional[_Union[_message_pb2.ResponseStatus, _Mapping]] = ...,
        meta: _Optional[_Union[AuditMetadata, _Mapping]] = ...,
    ) -> None: ...

class UnbindRequest(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: UnbindRequestBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[UnbindRequestBody, _Mapping]] = ...,
    ) -> None: ...

class UnbindRequestBody(_message.Message):
    __slots__ = ("uid",)
    UID_FIELD_NUMBER: _ClassVar[int]
    uid: str
    def __init__(self, uid: _Optional[str] = ...) -> None: ...

class UnbindResponse(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: UnbindResponseBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[UnbindResponseBody, _Mapping]] = ...,
    ) -> None: ...

class UnbindResponseBody(_message.Message):
    __slots__ = ("status",)
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: _message_pb2.ResponseStatus
    def __init__(self, status: _Optional[_Union[_message_pb2.ResponseStatus, _Mapping]] = ...) -> None: ...

class AuditRequest(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: AuditRequestBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[AuditRequestBody, _Mapping]] = ...,
    ) -> None: ...

class AuditRequestBody(_message.Message):
    __slots__ = ("uid", "status")
    UID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    uid: str
    status: AuditStatus
    def __init__(self, uid: _Optional[str] = ..., status: _Optional[_Union[AuditStatus, _Mapping]] = ...) -> None: ...

class AuditResponse(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: AuditResponseBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[AuditResponseBody, _Mapping]] = ...,
    ) -> None: ...

class AuditResponseBody(_message.Message):
    __slots__ = ("status", "meta")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    META_FIELD_NUMBER: _ClassVar[int]
    status: _message_pb2.ResponseStatus
    meta: AuditMetadata
    def __init__(
        self,
        status: _Optional[_Union[_message_pb2.ResponseStatus, _Mapping]] = ...,
        meta: _Optional[_Union[AuditMetadata, _Mapping]] = ...,
    ) -> None: ...

class CreateAuditListRequest(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: CreateAuditListRequestBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[CreateAuditListRequestBody, _Mapping]] = ...,
    ) -> None: ...

class CreateAuditListRequestBody(_message.Message):
    __slots__ = ("condition", "page")
    CONDITION_FIELD_NUMBER: _ClassVar[int]
    PAGE_FIELD_NUMBER: _ClassVar[int]
    condition: AuditSearchCondition
    page: _message_pb2.RequestPage
    def __init__(
        self,
        condition: _Optional[_Union[AuditSearchCondition, _Mapping]] = ...,
        page: _Optional[_Union[_message_pb2.RequestPage, _Mapping]] = ...,
    ) -> None: ...

class CreateAuditListResponse(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: CreateAuditListResponseBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[CreateAuditListResponseBody, _Mapping]] = ...,
    ) -> None: ...

class CreateAuditListResponseBody(_message.Message):
    __slots__ = ("status", "audits", "page")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    AUDITS_FIELD_NUMBER: _ClassVar[int]
    PAGE_FIELD_NUMBER: _ClassVar[int]
    status: _message_pb2.ResponseStatus
    audits: _containers.RepeatedCompositeFieldContainer[AuditMetadata]
    page: _message_pb2.ResponsePage
    def __init__(
        self,
        status: _Optional[_Union[_message_pb2.ResponseStatus, _Mapping]] = ...,
        audits: _Optional[_Iterable[_Union[AuditMetadata, _Mapping]]] = ...,
        page: _Optional[_Union[_message_pb2.ResponsePage, _Mapping]] = ...,
    ) -> None: ...

class AuditListRequest(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: AuditListRequestBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[AuditListRequestBody, _Mapping]] = ...,
    ) -> None: ...

class AuditListRequestBody(_message.Message):
    __slots__ = ("condition", "page")
    CONDITION_FIELD_NUMBER: _ClassVar[int]
    PAGE_FIELD_NUMBER: _ClassVar[int]
    condition: AuditSearchCondition
    page: _message_pb2.RequestPage
    def __init__(
        self,
        condition: _Optional[_Union[AuditSearchCondition, _Mapping]] = ...,
        page: _Optional[_Union[_message_pb2.RequestPage, _Mapping]] = ...,
    ) -> None: ...

class AuditListResponse(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: AuditListResponseBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[AuditListResponseBody, _Mapping]] = ...,
    ) -> None: ...

class AuditListResponseBody(_message.Message):
    __slots__ = ("status", "audits", "page")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    AUDITS_FIELD_NUMBER: _ClassVar[int]
    PAGE_FIELD_NUMBER: _ClassVar[int]
    status: _message_pb2.ResponseStatus
    audits: _containers.RepeatedCompositeFieldContainer[AuditMetadata]
    page: _message_pb2.ResponsePage
    def __init__(
        self,
        status: _Optional[_Union[_message_pb2.ResponseStatus, _Mapping]] = ...,
        audits: _Optional[_Iterable[_Union[AuditMetadata, _Mapping]]] = ...,
        page: _Optional[_Union[_message_pb2.ResponsePage, _Mapping]] = ...,
    ) -> None: ...

class AuditSearchCondition(_message.Message):
    __slots__ = ("sourceDid", "name", "startTime", "endTime", "type", "targetDid")
    SOURCEDID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    STARTTIME_FIELD_NUMBER: _ClassVar[int]
    ENDTIME_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    TARGETDID_FIELD_NUMBER: _ClassVar[int]
    sourceDid: str
    name: str
    startTime: str
    endTime: str
    type: _code_pb2.AuditTypeEnum
    targetDid: str
    def __init__(
        self,
        sourceDid: _Optional[str] = ...,
        name: _Optional[str] = ...,
        startTime: _Optional[str] = ...,
        endTime: _Optional[str] = ...,
        type: _Optional[_Union[_code_pb2.AuditTypeEnum, str]] = ...,
        targetDid: _Optional[str] = ...,
    ) -> None: ...

class AuditMetadata(_message.Message):
    __slots__ = (
        "uid",
        "appName",
        "sourceDid",
        "sourceName",
        "targetDid",
        "targetName",
        "reason",
        "status",
        "createdAt",
        "updatedAt",
        "type",
    )
    UID_FIELD_NUMBER: _ClassVar[int]
    APPNAME_FIELD_NUMBER: _ClassVar[int]
    SOURCEDID_FIELD_NUMBER: _ClassVar[int]
    SOURCENAME_FIELD_NUMBER: _ClassVar[int]
    TARGETDID_FIELD_NUMBER: _ClassVar[int]
    TARGETNAME_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    CREATEDAT_FIELD_NUMBER: _ClassVar[int]
    UPDATEDAT_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    uid: str
    appName: str
    sourceDid: str
    sourceName: str
    targetDid: str
    targetName: str
    reason: str
    status: AuditStatus
    createdAt: str
    updatedAt: str
    type: _code_pb2.AuditTypeEnum
    def __init__(
        self,
        uid: _Optional[str] = ...,
        appName: _Optional[str] = ...,
        sourceDid: _Optional[str] = ...,
        sourceName: _Optional[str] = ...,
        targetDid: _Optional[str] = ...,
        targetName: _Optional[str] = ...,
        reason: _Optional[str] = ...,
        status: _Optional[_Union[AuditStatus, _Mapping]] = ...,
        createdAt: _Optional[str] = ...,
        updatedAt: _Optional[str] = ...,
        type: _Optional[_Union[_code_pb2.AuditTypeEnum, str]] = ...,
    ) -> None: ...
