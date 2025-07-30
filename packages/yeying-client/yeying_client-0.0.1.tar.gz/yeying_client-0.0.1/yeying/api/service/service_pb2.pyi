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

class CreateServiceRequest(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: CreateServiceRequestBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[CreateServiceRequestBody, _Mapping]] = ...,
    ) -> None: ...

class CreateServiceRequestBody(_message.Message):
    __slots__ = ("service",)
    SERVICE_FIELD_NUMBER: _ClassVar[int]
    service: _model_pb2.ServiceMetadata
    def __init__(self, service: _Optional[_Union[_model_pb2.ServiceMetadata, _Mapping]] = ...) -> None: ...

class CreateServiceResponse(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: CreateServiceResponseBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[CreateServiceResponseBody, _Mapping]] = ...,
    ) -> None: ...

class CreateServiceResponseBody(_message.Message):
    __slots__ = ("status", "service")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    SERVICE_FIELD_NUMBER: _ClassVar[int]
    status: _message_pb2.ResponseStatus
    service: _model_pb2.ServiceMetadata
    def __init__(
        self,
        status: _Optional[_Union[_message_pb2.ResponseStatus, _Mapping]] = ...,
        service: _Optional[_Union[_model_pb2.ServiceMetadata, _Mapping]] = ...,
    ) -> None: ...

class DetailServiceRequest(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: DetailServiceRequestBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[DetailServiceRequestBody, _Mapping]] = ...,
    ) -> None: ...

class DetailServiceRequestBody(_message.Message):
    __slots__ = ("did", "version")
    DID_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    did: str
    version: int
    def __init__(self, did: _Optional[str] = ..., version: _Optional[int] = ...) -> None: ...

class DetailServiceResponse(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: DetailServiceResponseBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[DetailServiceResponseBody, _Mapping]] = ...,
    ) -> None: ...

class DetailServiceResponseBody(_message.Message):
    __slots__ = ("status", "service")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    SERVICE_FIELD_NUMBER: _ClassVar[int]
    status: _message_pb2.ResponseStatus
    service: _model_pb2.ServiceMetadata
    def __init__(
        self,
        status: _Optional[_Union[_message_pb2.ResponseStatus, _Mapping]] = ...,
        service: _Optional[_Union[_model_pb2.ServiceMetadata, _Mapping]] = ...,
    ) -> None: ...

class SearchServiceRequest(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: SearchServiceRequestBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[SearchServiceRequestBody, _Mapping]] = ...,
    ) -> None: ...

class SearchServiceRequestBody(_message.Message):
    __slots__ = ("condition", "page")
    CONDITION_FIELD_NUMBER: _ClassVar[int]
    PAGE_FIELD_NUMBER: _ClassVar[int]
    condition: SearchServiceCondition
    page: _message_pb2.RequestPage
    def __init__(
        self,
        condition: _Optional[_Union[SearchServiceCondition, _Mapping]] = ...,
        page: _Optional[_Union[_message_pb2.RequestPage, _Mapping]] = ...,
    ) -> None: ...

class SearchServiceCondition(_message.Message):
    __slots__ = ("code", "owner", "name", "keyword")
    CODE_FIELD_NUMBER: _ClassVar[int]
    OWNER_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    KEYWORD_FIELD_NUMBER: _ClassVar[int]
    code: _code_pb2.ServiceCodeEnum
    owner: str
    name: str
    keyword: str
    def __init__(
        self,
        code: _Optional[_Union[_code_pb2.ServiceCodeEnum, str]] = ...,
        owner: _Optional[str] = ...,
        name: _Optional[str] = ...,
        keyword: _Optional[str] = ...,
    ) -> None: ...

class SearchServiceResponse(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: SearchServiceResponseBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[SearchServiceResponseBody, _Mapping]] = ...,
    ) -> None: ...

class SearchServiceResponseBody(_message.Message):
    __slots__ = ("status", "services", "page")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    SERVICES_FIELD_NUMBER: _ClassVar[int]
    PAGE_FIELD_NUMBER: _ClassVar[int]
    status: _message_pb2.ResponseStatus
    services: _containers.RepeatedCompositeFieldContainer[_model_pb2.ServiceMetadata]
    page: _message_pb2.ResponsePage
    def __init__(
        self,
        status: _Optional[_Union[_message_pb2.ResponseStatus, _Mapping]] = ...,
        services: _Optional[_Iterable[_Union[_model_pb2.ServiceMetadata, _Mapping]]] = ...,
        page: _Optional[_Union[_message_pb2.ResponsePage, _Mapping]] = ...,
    ) -> None: ...

class OnlineServiceRequest(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: OnlineServiceRequestBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[OnlineServiceRequestBody, _Mapping]] = ...,
    ) -> None: ...

class OnlineServiceRequestBody(_message.Message):
    __slots__ = ("did", "version")
    DID_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    did: str
    version: int
    def __init__(self, did: _Optional[str] = ..., version: _Optional[int] = ...) -> None: ...

class OnlineServiceResponse(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: OnlineServiceResponseBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[OnlineServiceResponseBody, _Mapping]] = ...,
    ) -> None: ...

class OnlineServiceResponseBody(_message.Message):
    __slots__ = ("status", "service")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    SERVICE_FIELD_NUMBER: _ClassVar[int]
    status: _message_pb2.ResponseStatus
    service: _model_pb2.ServiceMetadata
    def __init__(
        self,
        status: _Optional[_Union[_message_pb2.ResponseStatus, _Mapping]] = ...,
        service: _Optional[_Union[_model_pb2.ServiceMetadata, _Mapping]] = ...,
    ) -> None: ...

class OfflineServiceRequest(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: OfflineServiceRequestBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[OfflineServiceRequestBody, _Mapping]] = ...,
    ) -> None: ...

class OfflineServiceRequestBody(_message.Message):
    __slots__ = ("did", "version")
    DID_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    did: str
    version: int
    def __init__(self, did: _Optional[str] = ..., version: _Optional[int] = ...) -> None: ...

class OfflineServiceResponse(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: OfflineServiceResponseBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[OfflineServiceResponseBody, _Mapping]] = ...,
    ) -> None: ...

class OfflineServiceResponseBody(_message.Message):
    __slots__ = ("status", "service")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    SERVICE_FIELD_NUMBER: _ClassVar[int]
    status: _message_pb2.ResponseStatus
    service: _model_pb2.ServiceMetadata
    def __init__(
        self,
        status: _Optional[_Union[_message_pb2.ResponseStatus, _Mapping]] = ...,
        service: _Optional[_Union[_model_pb2.ServiceMetadata, _Mapping]] = ...,
    ) -> None: ...

class DeleteServiceRequest(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: DeleteServiceRequestBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[DeleteServiceRequestBody, _Mapping]] = ...,
    ) -> None: ...

class DeleteServiceRequestBody(_message.Message):
    __slots__ = ("did", "version")
    DID_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    did: str
    version: int
    def __init__(self, did: _Optional[str] = ..., version: _Optional[int] = ...) -> None: ...

class DeleteServiceResponse(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: DeleteServiceResponseBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[DeleteServiceResponseBody, _Mapping]] = ...,
    ) -> None: ...

class DeleteServiceResponseBody(_message.Message):
    __slots__ = ("status",)
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: _message_pb2.ResponseStatus
    def __init__(self, status: _Optional[_Union[_message_pb2.ResponseStatus, _Mapping]] = ...) -> None: ...
