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

class SearchApplicationRequest(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: SearchApplicationRequestBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[SearchApplicationRequestBody, _Mapping]] = ...,
    ) -> None: ...

class SearchApplicationRequestBody(_message.Message):
    __slots__ = ("condition", "page")
    CONDITION_FIELD_NUMBER: _ClassVar[int]
    PAGE_FIELD_NUMBER: _ClassVar[int]
    condition: SearchCondition
    page: _message_pb2.RequestPage
    def __init__(
        self,
        condition: _Optional[_Union[SearchCondition, _Mapping]] = ...,
        page: _Optional[_Union[_message_pb2.RequestPage, _Mapping]] = ...,
    ) -> None: ...

class SearchCondition(_message.Message):
    __slots__ = ("code", "status", "owner", "name", "keyword")
    CODE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    OWNER_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    KEYWORD_FIELD_NUMBER: _ClassVar[int]
    code: _code_pb2.ApplicationCodeEnum
    status: _code_pb2.ApplicationStatusEnum
    owner: str
    name: str
    keyword: str
    def __init__(
        self,
        code: _Optional[_Union[_code_pb2.ApplicationCodeEnum, str]] = ...,
        status: _Optional[_Union[_code_pb2.ApplicationStatusEnum, str]] = ...,
        owner: _Optional[str] = ...,
        name: _Optional[str] = ...,
        keyword: _Optional[str] = ...,
    ) -> None: ...

class SearchApplicationResponse(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: SearchApplicationResponseBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[SearchApplicationResponseBody, _Mapping]] = ...,
    ) -> None: ...

class SearchApplicationResponseBody(_message.Message):
    __slots__ = ("status", "applications", "page")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    APPLICATIONS_FIELD_NUMBER: _ClassVar[int]
    PAGE_FIELD_NUMBER: _ClassVar[int]
    status: _message_pb2.ResponseStatus
    applications: _containers.RepeatedCompositeFieldContainer[_model_pb2.ApplicationMetadata]
    page: _message_pb2.ResponsePage
    def __init__(
        self,
        status: _Optional[_Union[_message_pb2.ResponseStatus, _Mapping]] = ...,
        applications: _Optional[_Iterable[_Union[_model_pb2.ApplicationMetadata, _Mapping]]] = ...,
        page: _Optional[_Union[_message_pb2.ResponsePage, _Mapping]] = ...,
    ) -> None: ...

class CreateApplicationRequest(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: CreateApplicationRequestBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[CreateApplicationRequestBody, _Mapping]] = ...,
    ) -> None: ...

class CreateApplicationRequestBody(_message.Message):
    __slots__ = ("application",)
    APPLICATION_FIELD_NUMBER: _ClassVar[int]
    application: _model_pb2.ApplicationMetadata
    def __init__(self, application: _Optional[_Union[_model_pb2.ApplicationMetadata, _Mapping]] = ...) -> None: ...

class CreateApplicationResponse(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: CreateApplicationResponseBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[CreateApplicationResponseBody, _Mapping]] = ...,
    ) -> None: ...

class CreateApplicationResponseBody(_message.Message):
    __slots__ = ("status", "application")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    APPLICATION_FIELD_NUMBER: _ClassVar[int]
    status: _message_pb2.ResponseStatus
    application: _model_pb2.ApplicationMetadata
    def __init__(
        self,
        status: _Optional[_Union[_message_pb2.ResponseStatus, _Mapping]] = ...,
        application: _Optional[_Union[_model_pb2.ApplicationMetadata, _Mapping]] = ...,
    ) -> None: ...

class ApplicationDetailRequest(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: ApplicationDetailRequestBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[ApplicationDetailRequestBody, _Mapping]] = ...,
    ) -> None: ...

class ApplicationDetailRequestBody(_message.Message):
    __slots__ = ("did", "version")
    DID_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    did: str
    version: int
    def __init__(self, did: _Optional[str] = ..., version: _Optional[int] = ...) -> None: ...

class ApplicationDetailResponse(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: ApplicationDetailResponseBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[ApplicationDetailResponseBody, _Mapping]] = ...,
    ) -> None: ...

class ApplicationDetailResponseBody(_message.Message):
    __slots__ = ("status", "application")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    APPLICATION_FIELD_NUMBER: _ClassVar[int]
    status: _message_pb2.ResponseStatus
    application: _model_pb2.ApplicationMetadata
    def __init__(
        self,
        status: _Optional[_Union[_message_pb2.ResponseStatus, _Mapping]] = ...,
        application: _Optional[_Union[_model_pb2.ApplicationMetadata, _Mapping]] = ...,
    ) -> None: ...

class OfflineApplicationRequest(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: OfflineApplicationRequestBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[OfflineApplicationRequestBody, _Mapping]] = ...,
    ) -> None: ...

class OfflineApplicationRequestBody(_message.Message):
    __slots__ = ("did", "version")
    DID_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    did: str
    version: int
    def __init__(self, did: _Optional[str] = ..., version: _Optional[int] = ...) -> None: ...

class OfflineApplicationResponse(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: OfflineApplicationResponseBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[OfflineApplicationResponseBody, _Mapping]] = ...,
    ) -> None: ...

class OfflineApplicationResponseBody(_message.Message):
    __slots__ = ("status",)
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: _message_pb2.ResponseStatus
    def __init__(self, status: _Optional[_Union[_message_pb2.ResponseStatus, _Mapping]] = ...) -> None: ...

class OnlineApplicationRequest(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: OnlineApplicationRequestBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[OnlineApplicationRequestBody, _Mapping]] = ...,
    ) -> None: ...

class OnlineApplicationRequestBody(_message.Message):
    __slots__ = ("did", "version")
    DID_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    did: str
    version: int
    def __init__(self, did: _Optional[str] = ..., version: _Optional[int] = ...) -> None: ...

class OnlineApplicationResponse(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: OnlineApplicationResponseBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[OnlineApplicationResponseBody, _Mapping]] = ...,
    ) -> None: ...

class OnlineApplicationResponseBody(_message.Message):
    __slots__ = ("status",)
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: _message_pb2.ResponseStatus
    def __init__(self, status: _Optional[_Union[_message_pb2.ResponseStatus, _Mapping]] = ...) -> None: ...

class ApplicationExtend(_message.Message):
    __slots__ = ("comments",)
    COMMENTS_FIELD_NUMBER: _ClassVar[int]
    comments: _containers.RepeatedCompositeFieldContainer[ApplicationComment]
    def __init__(self, comments: _Optional[_Iterable[_Union[ApplicationComment, _Mapping]]] = ...) -> None: ...

class ApplicationComment(_message.Message):
    __slots__ = ("auditor", "comment", "passed", "signature")
    AUDITOR_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    PASSED_FIELD_NUMBER: _ClassVar[int]
    SIGNATURE_FIELD_NUMBER: _ClassVar[int]
    auditor: str
    comment: str
    passed: bool
    signature: str
    def __init__(
        self,
        auditor: _Optional[str] = ...,
        comment: _Optional[str] = ...,
        passed: bool = ...,
        signature: _Optional[str] = ...,
    ) -> None: ...

class DeleteApplicationRequest(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: DeleteApplicationRequestBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[DeleteApplicationRequestBody, _Mapping]] = ...,
    ) -> None: ...

class DeleteApplicationRequestBody(_message.Message):
    __slots__ = ("did", "version")
    DID_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    did: str
    version: int
    def __init__(self, did: _Optional[str] = ..., version: _Optional[int] = ...) -> None: ...

class DeleteApplicationResponse(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: DeleteApplicationResponseBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[DeleteApplicationResponseBody, _Mapping]] = ...,
    ) -> None: ...

class DeleteApplicationResponseBody(_message.Message):
    __slots__ = ("status",)
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: _message_pb2.ResponseStatus
    def __init__(self, status: _Optional[_Union[_message_pb2.ResponseStatus, _Mapping]] = ...) -> None: ...

class AuditApplicationRequest(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: AuditApplicationRequestBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[AuditApplicationRequestBody, _Mapping]] = ...,
    ) -> None: ...

class AuditApplicationRequestBody(_message.Message):
    __slots__ = ("comment", "did", "version")
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    DID_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    comment: ApplicationComment
    did: str
    version: int
    def __init__(
        self,
        comment: _Optional[_Union[ApplicationComment, _Mapping]] = ...,
        did: _Optional[str] = ...,
        version: _Optional[int] = ...,
    ) -> None: ...

class AuditApplicationResponse(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: AuditApplicationResponseBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[AuditApplicationResponseBody, _Mapping]] = ...,
    ) -> None: ...

class AuditApplicationResponseBody(_message.Message):
    __slots__ = ("status",)
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: _message_pb2.ResponseStatus
    def __init__(self, status: _Optional[_Union[_message_pb2.ResponseStatus, _Mapping]] = ...) -> None: ...
