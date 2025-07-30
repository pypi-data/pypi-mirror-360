from yeying.api.common import message_pb2 as _message_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SendMailRequest(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: SendMailRequestBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[SendMailRequestBody, _Mapping]] = ...,
    ) -> None: ...

class SendMailRequestBody(_message.Message):
    __slots__ = ("toMail",)
    TOMAIL_FIELD_NUMBER: _ClassVar[int]
    toMail: str
    def __init__(self, toMail: _Optional[str] = ...) -> None: ...

class SendMailResponse(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: SendMailResponseBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[SendMailResponseBody, _Mapping]] = ...,
    ) -> None: ...

class SendMailResponseBody(_message.Message):
    __slots__ = ("status",)
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: _message_pb2.ResponseStatus
    def __init__(self, status: _Optional[_Union[_message_pb2.ResponseStatus, _Mapping]] = ...) -> None: ...

class VerifyMailRequest(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: VerifyMailRequestBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[VerifyMailRequestBody, _Mapping]] = ...,
    ) -> None: ...

class VerifyMailRequestBody(_message.Message):
    __slots__ = ("toMail", "code")
    TOMAIL_FIELD_NUMBER: _ClassVar[int]
    CODE_FIELD_NUMBER: _ClassVar[int]
    toMail: str
    code: str
    def __init__(self, toMail: _Optional[str] = ..., code: _Optional[str] = ...) -> None: ...

class VerifyMailResponse(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: VerifyMailResponseBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[VerifyMailResponseBody, _Mapping]] = ...,
    ) -> None: ...

class VerifyMailResponseBody(_message.Message):
    __slots__ = ("status",)
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: _message_pb2.ResponseStatus
    def __init__(self, status: _Optional[_Union[_message_pb2.ResponseStatus, _Mapping]] = ...) -> None: ...
