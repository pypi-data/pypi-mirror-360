from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from typing import ClassVar as _ClassVar

DESCRIPTOR: _descriptor.FileDescriptor

class ImageContentTypeEnum(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    QUESTION: _ClassVar[ImageContentTypeEnum]
    ANSWER: _ClassVar[ImageContentTypeEnum]
    QA: _ClassVar[ImageContentTypeEnum]

class TaskStatusEnum(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    CREATED: _ClassVar[TaskStatusEnum]
    WAIT_MARKING: _ClassVar[TaskStatusEnum]
    MARKING: _ClassVar[TaskStatusEnum]
    FINISH_MARKING: _ClassVar[TaskStatusEnum]
    WAIT_REVISE: _ClassVar[TaskStatusEnum]
    REVISE: _ClassVar[TaskStatusEnum]
    FINISH_REVISE: _ClassVar[TaskStatusEnum]

QUESTION: ImageContentTypeEnum
ANSWER: ImageContentTypeEnum
QA: ImageContentTypeEnum
CREATED: TaskStatusEnum
WAIT_MARKING: TaskStatusEnum
MARKING: TaskStatusEnum
FINISH_MARKING: TaskStatusEnum
WAIT_REVISE: TaskStatusEnum
REVISE: TaskStatusEnum
FINISH_REVISE: TaskStatusEnum
