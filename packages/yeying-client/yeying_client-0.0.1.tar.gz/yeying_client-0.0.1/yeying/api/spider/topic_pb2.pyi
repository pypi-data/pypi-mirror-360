from yeying.api.common import message_pb2 as _message_pb2
from yeying.api.common import code_pb2 as _code_pb2
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

class SearchRequest(_message.Message):
    __slots__ = ("owner",)
    OWNER_FIELD_NUMBER: _ClassVar[int]
    owner: str
    def __init__(self, owner: _Optional[str] = ...) -> None: ...

class SearchResponse(_message.Message):
    __slots__ = ("status", "topicMetadata")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    TOPICMETADATA_FIELD_NUMBER: _ClassVar[int]
    status: _message_pb2.ResponseStatus
    topicMetadata: _containers.RepeatedCompositeFieldContainer[TopicMetadata]
    def __init__(
        self,
        status: _Optional[_Union[_message_pb2.ResponseStatus, _Mapping]] = ...,
        topicMetadata: _Optional[_Iterable[_Union[TopicMetadata, _Mapping]]] = ...,
    ) -> None: ...

class UnsubscribeRequest(_message.Message):
    __slots__ = ("owner", "name")
    OWNER_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    owner: str
    name: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, owner: _Optional[str] = ..., name: _Optional[_Iterable[str]] = ...) -> None: ...

class UnsubscribeResponse(_message.Message):
    __slots__ = ("status",)
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: _message_pb2.ResponseStatus
    def __init__(self, status: _Optional[_Union[_message_pb2.ResponseStatus, _Mapping]] = ...) -> None: ...

class TopicMetadata(_message.Message):
    __slots__ = ("name", "format", "expression", "status")
    NAME_FIELD_NUMBER: _ClassVar[int]
    FORMAT_FIELD_NUMBER: _ClassVar[int]
    EXPRESSION_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    name: str
    format: _containers.RepeatedScalarFieldContainer[_code_pb2.DigitalFormatEnum]
    expression: str
    status: _code_pb2.ContractStatusEnum
    def __init__(
        self,
        name: _Optional[str] = ...,
        format: _Optional[_Iterable[_Union[_code_pb2.DigitalFormatEnum, str]]] = ...,
        expression: _Optional[str] = ...,
        status: _Optional[_Union[_code_pb2.ContractStatusEnum, str]] = ...,
    ) -> None: ...

class SubscribeRequest(_message.Message):
    __slots__ = ("owner", "topicMetadata")
    OWNER_FIELD_NUMBER: _ClassVar[int]
    TOPICMETADATA_FIELD_NUMBER: _ClassVar[int]
    owner: str
    topicMetadata: _containers.RepeatedCompositeFieldContainer[TopicMetadata]
    def __init__(
        self, owner: _Optional[str] = ..., topicMetadata: _Optional[_Iterable[_Union[TopicMetadata, _Mapping]]] = ...
    ) -> None: ...

class SubscribeResponse(_message.Message):
    __slots__ = ("status",)
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: _message_pb2.ResponseStatus
    def __init__(self, status: _Optional[_Union[_message_pb2.ResponseStatus, _Mapping]] = ...) -> None: ...
