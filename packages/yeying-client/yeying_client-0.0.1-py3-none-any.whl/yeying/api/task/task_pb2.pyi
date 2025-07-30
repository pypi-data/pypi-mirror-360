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

class TaskCodeEnum(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    TASK_CODE_UNKNOWN: _ClassVar[TaskCodeEnum]
    TASK_CODE_STATISTIC: _ClassVar[TaskCodeEnum]

TASK_CODE_UNKNOWN: TaskCodeEnum
TASK_CODE_STATISTIC: TaskCodeEnum

class CreateTaskRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class CreateTaskResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class TaskMetadata(_message.Message):
    __slots__ = ("uid", "code", "creator", "participant", "terminator", "createdAt", "content")
    UID_FIELD_NUMBER: _ClassVar[int]
    CODE_FIELD_NUMBER: _ClassVar[int]
    CREATOR_FIELD_NUMBER: _ClassVar[int]
    PARTICIPANT_FIELD_NUMBER: _ClassVar[int]
    TERMINATOR_FIELD_NUMBER: _ClassVar[int]
    CREATEDAT_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    uid: str
    code: TaskCodeEnum
    creator: str
    participant: str
    terminator: str
    createdAt: str
    content: str
    def __init__(
        self,
        uid: _Optional[str] = ...,
        code: _Optional[_Union[TaskCodeEnum, str]] = ...,
        creator: _Optional[str] = ...,
        participant: _Optional[str] = ...,
        terminator: _Optional[str] = ...,
        createdAt: _Optional[str] = ...,
        content: _Optional[str] = ...,
    ) -> None: ...

class FetchTaskResponse(_message.Message):
    __slots__ = ("tasks",)
    TASKS_FIELD_NUMBER: _ClassVar[int]
    tasks: _containers.RepeatedCompositeFieldContainer[TaskMetadata]
    def __init__(self, tasks: _Optional[_Iterable[_Union[TaskMetadata, _Mapping]]] = ...) -> None: ...
