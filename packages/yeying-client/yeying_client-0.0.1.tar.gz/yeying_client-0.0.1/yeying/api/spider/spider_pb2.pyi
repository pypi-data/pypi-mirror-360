from yeying.api.common import message_pb2 as _message_pb2
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

class PluginType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    WEB: _ClassVar[PluginType]
    SPIDER: _ClassVar[PluginType]

WEB: PluginType
SPIDER: PluginType

class SearchRequest(_message.Message):
    __slots__ = ("owner", "conditionList")
    OWNER_FIELD_NUMBER: _ClassVar[int]
    CONDITIONLIST_FIELD_NUMBER: _ClassVar[int]
    owner: str
    conditionList: _containers.RepeatedCompositeFieldContainer[Condition]
    def __init__(
        self, owner: _Optional[str] = ..., conditionList: _Optional[_Iterable[_Union[Condition, _Mapping]]] = ...
    ) -> None: ...

class Condition(_message.Message):
    __slots__ = ("sql",)
    SQL_FIELD_NUMBER: _ClassVar[int]
    sql: str
    def __init__(self, sql: _Optional[str] = ...) -> None: ...

class SearchResponse(_message.Message):
    __slots__ = ("pluginItemList",)
    PLUGINITEMLIST_FIELD_NUMBER: _ClassVar[int]
    pluginItemList: _containers.RepeatedCompositeFieldContainer[PluginItem]
    def __init__(self, pluginItemList: _Optional[_Iterable[_Union[PluginItem, _Mapping]]] = ...) -> None: ...

class PluginItem(_message.Message):
    __slots__ = ("name", "description", "version", "code", "timestamp")
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    CODE_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    name: str
    description: str
    version: str
    code: str
    timestamp: int
    def __init__(
        self,
        name: _Optional[str] = ...,
        description: _Optional[str] = ...,
        version: _Optional[str] = ...,
        code: _Optional[str] = ...,
        timestamp: _Optional[int] = ...,
    ) -> None: ...

class InstallRequest(_message.Message):
    __slots__ = ("owner", "version", "name", "description", "code", "extend")
    OWNER_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    CODE_FIELD_NUMBER: _ClassVar[int]
    EXTEND_FIELD_NUMBER: _ClassVar[int]
    owner: str
    version: str
    name: str
    description: str
    code: str
    extend: str
    def __init__(
        self,
        owner: _Optional[str] = ...,
        version: _Optional[str] = ...,
        name: _Optional[str] = ...,
        description: _Optional[str] = ...,
        code: _Optional[str] = ...,
        extend: _Optional[str] = ...,
    ) -> None: ...

class UninstallRequest(_message.Message):
    __slots__ = ("owner", "name")
    OWNER_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    owner: str
    name: str
    def __init__(self, owner: _Optional[str] = ..., name: _Optional[str] = ...) -> None: ...

class UninstallResponse(_message.Message):
    __slots__ = ("responseStatus",)
    RESPONSESTATUS_FIELD_NUMBER: _ClassVar[int]
    responseStatus: _message_pb2.ResponseStatus
    def __init__(self, responseStatus: _Optional[_Union[_message_pb2.ResponseStatus, _Mapping]] = ...) -> None: ...

class InstallResponse(_message.Message):
    __slots__ = ("responseStatus",)
    RESPONSESTATUS_FIELD_NUMBER: _ClassVar[int]
    responseStatus: _message_pb2.ResponseStatus
    def __init__(self, responseStatus: _Optional[_Union[_message_pb2.ResponseStatus, _Mapping]] = ...) -> None: ...
