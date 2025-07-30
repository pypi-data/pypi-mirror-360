from yeying.api.common import message_pb2 as _message_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SignRequest(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: SignRequestBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[SignRequestBody, _Mapping]] = ...,
    ) -> None: ...

class SignRequestBody(_message.Message):
    __slots__ = ("domain", "csr")
    DOMAIN_FIELD_NUMBER: _ClassVar[int]
    CSR_FIELD_NUMBER: _ClassVar[int]
    domain: str
    csr: str
    def __init__(self, domain: _Optional[str] = ..., csr: _Optional[str] = ...) -> None: ...

class SignResponse(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: SignResponseBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[SignResponseBody, _Mapping]] = ...,
    ) -> None: ...

class CertificateMetadata(_message.Message):
    __slots__ = ("crt", "ca")
    CRT_FIELD_NUMBER: _ClassVar[int]
    CA_FIELD_NUMBER: _ClassVar[int]
    crt: str
    ca: str
    def __init__(self, crt: _Optional[str] = ..., ca: _Optional[str] = ...) -> None: ...

class SignResponseBody(_message.Message):
    __slots__ = ("status", "certificate")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    CERTIFICATE_FIELD_NUMBER: _ClassVar[int]
    status: _message_pb2.ResponseStatus
    certificate: CertificateMetadata
    def __init__(
        self,
        status: _Optional[_Union[_message_pb2.ResponseStatus, _Mapping]] = ...,
        certificate: _Optional[_Union[CertificateMetadata, _Mapping]] = ...,
    ) -> None: ...

class GetRequest(_message.Message):
    __slots__ = ("header",)
    HEADER_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    def __init__(self, header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...) -> None: ...

class GetResponse(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: GetResponseBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[GetResponseBody, _Mapping]] = ...,
    ) -> None: ...

class GetResponseBody(_message.Message):
    __slots__ = ("status", "certificate")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    CERTIFICATE_FIELD_NUMBER: _ClassVar[int]
    status: _message_pb2.ResponseStatus
    certificate: CertificateMetadata
    def __init__(
        self,
        status: _Optional[_Union[_message_pb2.ResponseStatus, _Mapping]] = ...,
        certificate: _Optional[_Union[CertificateMetadata, _Mapping]] = ...,
    ) -> None: ...
