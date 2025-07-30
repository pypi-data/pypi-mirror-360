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

class ContentType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ARTICLE: _ClassVar[ContentType]

ARTICLE: ContentType

class SearchRequest(_message.Message):
    __slots__ = ("articleMetadata",)
    ARTICLEMETADATA_FIELD_NUMBER: _ClassVar[int]
    articleMetadata: _containers.RepeatedCompositeFieldContainer[KnowledgeMetadata]
    def __init__(self, articleMetadata: _Optional[_Iterable[_Union[KnowledgeMetadata, _Mapping]]] = ...) -> None: ...

class SearchResponse(_message.Message):
    __slots__ = ("status",)
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: _message_pb2.ResponseStatus
    def __init__(self, status: _Optional[_Union[_message_pb2.ResponseStatus, _Mapping]] = ...) -> None: ...

class KnowledgeMetadata(_message.Message):
    __slots__ = ("format", "hash", "author", "source", "publishTime", "keyword", "summary", "content")
    FORMAT_FIELD_NUMBER: _ClassVar[int]
    HASH_FIELD_NUMBER: _ClassVar[int]
    AUTHOR_FIELD_NUMBER: _ClassVar[int]
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    PUBLISHTIME_FIELD_NUMBER: _ClassVar[int]
    KEYWORD_FIELD_NUMBER: _ClassVar[int]
    SUMMARY_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    format: _code_pb2.DigitalFormatEnum
    hash: str
    author: str
    source: str
    publishTime: str
    keyword: str
    summary: str
    content: str
    def __init__(
        self,
        format: _Optional[_Union[_code_pb2.DigitalFormatEnum, str]] = ...,
        hash: _Optional[str] = ...,
        author: _Optional[str] = ...,
        source: _Optional[str] = ...,
        publishTime: _Optional[str] = ...,
        keyword: _Optional[str] = ...,
        summary: _Optional[str] = ...,
        content: _Optional[str] = ...,
    ) -> None: ...

class AppendMetadata(_message.Message):
    __slots__ = ("hash", "subscriber", "content")
    HASH_FIELD_NUMBER: _ClassVar[int]
    SUBSCRIBER_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    hash: str
    subscriber: str
    content: str
    def __init__(
        self, hash: _Optional[str] = ..., subscriber: _Optional[str] = ..., content: _Optional[str] = ...
    ) -> None: ...

class AppendRequest(_message.Message):
    __slots__ = ("appendMetadata",)
    APPENDMETADATA_FIELD_NUMBER: _ClassVar[int]
    appendMetadata: _containers.RepeatedCompositeFieldContainer[AppendMetadata]
    def __init__(self, appendMetadata: _Optional[_Iterable[_Union[AppendMetadata, _Mapping]]] = ...) -> None: ...

class AppendResponse(_message.Message):
    __slots__ = ("status",)
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: _message_pb2.ResponseStatus
    def __init__(self, status: _Optional[_Union[_message_pb2.ResponseStatus, _Mapping]] = ...) -> None: ...
