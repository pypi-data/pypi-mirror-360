from yeying.api.common import message_pb2 as _message_pb2
from yeying.api.common import code_pb2 as _code_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
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

class BulletinCodeEnum(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    BULLETIN_CODE_SOLUTION: _ClassVar[BulletinCodeEnum]

BULLETIN_CODE_SOLUTION: BulletinCodeEnum

class BulletinListRequest(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: BulletinListRequestBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[BulletinListRequestBody, _Mapping]] = ...,
    ) -> None: ...

class BulletinListRequestBody(_message.Message):
    __slots__ = ("code", "language", "page")
    CODE_FIELD_NUMBER: _ClassVar[int]
    LANGUAGE_FIELD_NUMBER: _ClassVar[int]
    PAGE_FIELD_NUMBER: _ClassVar[int]
    code: BulletinCodeEnum
    language: _code_pb2.LanguageCodeEnum
    page: _message_pb2.RequestPage
    def __init__(
        self,
        code: _Optional[_Union[BulletinCodeEnum, str]] = ...,
        language: _Optional[_Union[_code_pb2.LanguageCodeEnum, str]] = ...,
        page: _Optional[_Union[_message_pb2.RequestPage, _Mapping]] = ...,
    ) -> None: ...

class BulletinListResponse(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: BulletinListResponseBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[BulletinListResponseBody, _Mapping]] = ...,
    ) -> None: ...

class BulletinListResponseBody(_message.Message):
    __slots__ = ("status", "solutions", "page")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    SOLUTIONS_FIELD_NUMBER: _ClassVar[int]
    PAGE_FIELD_NUMBER: _ClassVar[int]
    status: _message_pb2.ResponseStatus
    solutions: _containers.RepeatedCompositeFieldContainer[SolutionMetadata]
    page: _message_pb2.ResponsePage
    def __init__(
        self,
        status: _Optional[_Union[_message_pb2.ResponseStatus, _Mapping]] = ...,
        solutions: _Optional[_Iterable[_Union[SolutionMetadata, _Mapping]]] = ...,
        page: _Optional[_Union[_message_pb2.ResponsePage, _Mapping]] = ...,
    ) -> None: ...

class SolutionMetadata(_message.Message):
    __slots__ = ("publisher", "language", "uid", "name", "description", "createdAt", "cards", "signature")
    PUBLISHER_FIELD_NUMBER: _ClassVar[int]
    LANGUAGE_FIELD_NUMBER: _ClassVar[int]
    UID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    CREATEDAT_FIELD_NUMBER: _ClassVar[int]
    CARDS_FIELD_NUMBER: _ClassVar[int]
    SIGNATURE_FIELD_NUMBER: _ClassVar[int]
    publisher: str
    language: _code_pb2.LanguageCodeEnum
    uid: str
    name: str
    description: str
    createdAt: str
    cards: _containers.RepeatedCompositeFieldContainer[SolutionCard]
    signature: str
    def __init__(
        self,
        publisher: _Optional[str] = ...,
        language: _Optional[_Union[_code_pb2.LanguageCodeEnum, str]] = ...,
        uid: _Optional[str] = ...,
        name: _Optional[str] = ...,
        description: _Optional[str] = ...,
        createdAt: _Optional[str] = ...,
        cards: _Optional[_Iterable[_Union[SolutionCard, _Mapping]]] = ...,
        signature: _Optional[str] = ...,
    ) -> None: ...

class SolutionCard(_message.Message):
    __slots__ = ("name", "price", "variables")
    NAME_FIELD_NUMBER: _ClassVar[int]
    PRICE_FIELD_NUMBER: _ClassVar[int]
    VARIABLES_FIELD_NUMBER: _ClassVar[int]
    name: str
    price: str
    variables: str
    def __init__(
        self, name: _Optional[str] = ..., price: _Optional[str] = ..., variables: _Optional[str] = ...
    ) -> None: ...
