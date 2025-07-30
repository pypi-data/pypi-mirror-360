from yeying.api.common import message_pb2 as _message_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SupportCodeEnum(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SUPPORT_CODE_FAQ: _ClassVar[SupportCodeEnum]
    SUPPORT_CODE_CSR: _ClassVar[SupportCodeEnum]
    SUPPORT_CODE_IVR: _ClassVar[SupportCodeEnum]

SUPPORT_CODE_FAQ: SupportCodeEnum
SUPPORT_CODE_CSR: SupportCodeEnum
SUPPORT_CODE_IVR: SupportCodeEnum

class CollectSupportRequest(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: CollectSupportRequestBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[CollectSupportRequestBody, _Mapping]] = ...,
    ) -> None: ...

class CollectSupportRequestBody(_message.Message):
    __slots__ = ("code", "faq")
    CODE_FIELD_NUMBER: _ClassVar[int]
    FAQ_FIELD_NUMBER: _ClassVar[int]
    code: SupportCodeEnum
    faq: FaqMetadata
    def __init__(
        self, code: _Optional[_Union[SupportCodeEnum, str]] = ..., faq: _Optional[_Union[FaqMetadata, _Mapping]] = ...
    ) -> None: ...

class FaqMetadata(_message.Message):
    __slots__ = ("did", "email", "type", "description", "createdAt", "signature")
    DID_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    CREATEDAT_FIELD_NUMBER: _ClassVar[int]
    SIGNATURE_FIELD_NUMBER: _ClassVar[int]
    did: str
    email: str
    type: str
    description: str
    createdAt: str
    signature: str
    def __init__(
        self,
        did: _Optional[str] = ...,
        email: _Optional[str] = ...,
        type: _Optional[str] = ...,
        description: _Optional[str] = ...,
        createdAt: _Optional[str] = ...,
        signature: _Optional[str] = ...,
    ) -> None: ...

class CollectSupportResponse(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: CollectSupportResponseBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[CollectSupportResponseBody, _Mapping]] = ...,
    ) -> None: ...

class CollectSupportResponseBody(_message.Message):
    __slots__ = ("status",)
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: _message_pb2.ResponseStatus
    def __init__(self, status: _Optional[_Union[_message_pb2.ResponseStatus, _Mapping]] = ...) -> None: ...
