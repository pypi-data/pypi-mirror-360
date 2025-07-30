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

class EventTypeEnum(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    EVENT_TYPE_UNKNOWN: _ClassVar[EventTypeEnum]
    EVENT_TYPE_REMIND: _ClassVar[EventTypeEnum]
    EVENT_TYPE_NOTIFY: _ClassVar[EventTypeEnum]
    EVENT_TYPE_APPLY: _ClassVar[EventTypeEnum]
    EVENT_TYPE_CUSTOM: _ClassVar[EventTypeEnum]

class ApplyActionEnum(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    APPLY_ACTION_UNKNOWN: _ClassVar[ApplyActionEnum]
    APPLY_ACTION_PASSED: _ClassVar[ApplyActionEnum]
    APPLY_ACTION_REFUSED: _ClassVar[ApplyActionEnum]

class NotifyActionEnum(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    NOTIFY_ACTION_UNKNOWN: _ClassVar[NotifyActionEnum]
    NOTIFY_ACTION_ADD: _ClassVar[NotifyActionEnum]
    NOTIFY_ACTION_DEL: _ClassVar[NotifyActionEnum]
    NOTIFY_ACTION_MOD: _ClassVar[NotifyActionEnum]

EVENT_TYPE_UNKNOWN: EventTypeEnum
EVENT_TYPE_REMIND: EventTypeEnum
EVENT_TYPE_NOTIFY: EventTypeEnum
EVENT_TYPE_APPLY: EventTypeEnum
EVENT_TYPE_CUSTOM: EventTypeEnum
APPLY_ACTION_UNKNOWN: ApplyActionEnum
APPLY_ACTION_PASSED: ApplyActionEnum
APPLY_ACTION_REFUSED: ApplyActionEnum
NOTIFY_ACTION_UNKNOWN: NotifyActionEnum
NOTIFY_ACTION_ADD: NotifyActionEnum
NOTIFY_ACTION_DEL: NotifyActionEnum
NOTIFY_ACTION_MOD: NotifyActionEnum

class EventMetadata(_message.Message):
    __slots__ = (
        "uid",
        "type",
        "producers",
        "consumers",
        "signature",
        "extend",
        "createdAt",
        "processedAt",
        "notifyContent",
        "applyContent",
        "customContent",
        "notifyOpinion",
        "applyOpinion",
        "customOpinion",
    )
    UID_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    PRODUCERS_FIELD_NUMBER: _ClassVar[int]
    CONSUMERS_FIELD_NUMBER: _ClassVar[int]
    SIGNATURE_FIELD_NUMBER: _ClassVar[int]
    EXTEND_FIELD_NUMBER: _ClassVar[int]
    CREATEDAT_FIELD_NUMBER: _ClassVar[int]
    PROCESSEDAT_FIELD_NUMBER: _ClassVar[int]
    NOTIFYCONTENT_FIELD_NUMBER: _ClassVar[int]
    APPLYCONTENT_FIELD_NUMBER: _ClassVar[int]
    CUSTOMCONTENT_FIELD_NUMBER: _ClassVar[int]
    NOTIFYOPINION_FIELD_NUMBER: _ClassVar[int]
    APPLYOPINION_FIELD_NUMBER: _ClassVar[int]
    CUSTOMOPINION_FIELD_NUMBER: _ClassVar[int]
    uid: str
    type: EventTypeEnum
    producers: _containers.RepeatedScalarFieldContainer[str]
    consumers: _containers.RepeatedScalarFieldContainer[str]
    signature: EventSignature
    extend: str
    createdAt: str
    processedAt: str
    notifyContent: NotifyContent
    applyContent: ApplyContent
    customContent: CustomContent
    notifyOpinion: NotifyOpinion
    applyOpinion: ApplyOpinion
    customOpinion: CustomOpinion
    def __init__(
        self,
        uid: _Optional[str] = ...,
        type: _Optional[_Union[EventTypeEnum, str]] = ...,
        producers: _Optional[_Iterable[str]] = ...,
        consumers: _Optional[_Iterable[str]] = ...,
        signature: _Optional[_Union[EventSignature, _Mapping]] = ...,
        extend: _Optional[str] = ...,
        createdAt: _Optional[str] = ...,
        processedAt: _Optional[str] = ...,
        notifyContent: _Optional[_Union[NotifyContent, _Mapping]] = ...,
        applyContent: _Optional[_Union[ApplyContent, _Mapping]] = ...,
        customContent: _Optional[_Union[CustomContent, _Mapping]] = ...,
        notifyOpinion: _Optional[_Union[NotifyOpinion, _Mapping]] = ...,
        applyOpinion: _Optional[_Union[ApplyOpinion, _Mapping]] = ...,
        customOpinion: _Optional[_Union[CustomOpinion, _Mapping]] = ...,
    ) -> None: ...

class SignatureObject(_message.Message):
    __slots__ = (
        "uid",
        "type",
        "producers",
        "consumers",
        "signature",
        "extend",
        "createdAt",
        "processedAt",
        "opinion",
        "content",
    )
    UID_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    PRODUCERS_FIELD_NUMBER: _ClassVar[int]
    CONSUMERS_FIELD_NUMBER: _ClassVar[int]
    SIGNATURE_FIELD_NUMBER: _ClassVar[int]
    EXTEND_FIELD_NUMBER: _ClassVar[int]
    CREATEDAT_FIELD_NUMBER: _ClassVar[int]
    PROCESSEDAT_FIELD_NUMBER: _ClassVar[int]
    OPINION_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    uid: str
    type: EventTypeEnum
    producers: _containers.RepeatedScalarFieldContainer[str]
    consumers: _containers.RepeatedScalarFieldContainer[str]
    signature: bytes
    extend: str
    createdAt: str
    processedAt: str
    opinion: bytes
    content: bytes
    def __init__(
        self,
        uid: _Optional[str] = ...,
        type: _Optional[_Union[EventTypeEnum, str]] = ...,
        producers: _Optional[_Iterable[str]] = ...,
        consumers: _Optional[_Iterable[str]] = ...,
        signature: _Optional[bytes] = ...,
        extend: _Optional[str] = ...,
        createdAt: _Optional[str] = ...,
        processedAt: _Optional[str] = ...,
        opinion: _Optional[bytes] = ...,
        content: _Optional[bytes] = ...,
    ) -> None: ...

class EventSignature(_message.Message):
    __slots__ = ("producers", "consumers")
    PRODUCERS_FIELD_NUMBER: _ClassVar[int]
    CONSUMERS_FIELD_NUMBER: _ClassVar[int]
    producers: _containers.RepeatedScalarFieldContainer[str]
    consumers: _containers.RepeatedScalarFieldContainer[str]
    def __init__(
        self, producers: _Optional[_Iterable[str]] = ..., consumers: _Optional[_Iterable[str]] = ...
    ) -> None: ...

class CustomContent(_message.Message):
    __slots__ = ("name", "object")
    NAME_FIELD_NUMBER: _ClassVar[int]
    OBJECT_FIELD_NUMBER: _ClassVar[int]
    name: str
    object: str
    def __init__(self, name: _Optional[str] = ..., object: _Optional[str] = ...) -> None: ...

class ApplyContent(_message.Message):
    __slots__ = ("applier",)
    APPLIER_FIELD_NUMBER: _ClassVar[int]
    applier: str
    def __init__(self, applier: _Optional[str] = ...) -> None: ...

class NotifyContent(_message.Message):
    __slots__ = ("name", "items")
    NAME_FIELD_NUMBER: _ClassVar[int]
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    name: str
    items: _containers.RepeatedCompositeFieldContainer[NotifyItem]
    def __init__(
        self, name: _Optional[str] = ..., items: _Optional[_Iterable[_Union[NotifyItem, _Mapping]]] = ...
    ) -> None: ...

class NotifyItem(_message.Message):
    __slots__ = ("uid", "action")
    UID_FIELD_NUMBER: _ClassVar[int]
    ACTION_FIELD_NUMBER: _ClassVar[int]
    uid: str
    action: NotifyActionEnum
    def __init__(self, uid: _Optional[str] = ..., action: _Optional[_Union[NotifyActionEnum, str]] = ...) -> None: ...

class ProduceRequest(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: ProduceRequestBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[ProduceRequestBody, _Mapping]] = ...,
    ) -> None: ...

class ProduceRequestBody(_message.Message):
    __slots__ = ("event",)
    EVENT_FIELD_NUMBER: _ClassVar[int]
    event: EventMetadata
    def __init__(self, event: _Optional[_Union[EventMetadata, _Mapping]] = ...) -> None: ...

class ProduceResponse(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: ProduceResponseBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[ProduceResponseBody, _Mapping]] = ...,
    ) -> None: ...

class ProduceResponseBody(_message.Message):
    __slots__ = ("status",)
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: _message_pb2.ResponseStatus
    def __init__(self, status: _Optional[_Union[_message_pb2.ResponseStatus, _Mapping]] = ...) -> None: ...

class ConsumeRequest(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: ConsumeRequestBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[ConsumeRequestBody, _Mapping]] = ...,
    ) -> None: ...

class ConsumeRequestBody(_message.Message):
    __slots__ = ("metadata",)
    METADATA_FIELD_NUMBER: _ClassVar[int]
    metadata: EventMetadata
    def __init__(self, metadata: _Optional[_Union[EventMetadata, _Mapping]] = ...) -> None: ...

class NotifyOpinion(_message.Message):
    __slots__ = ("processed",)
    PROCESSED_FIELD_NUMBER: _ClassVar[int]
    processed: str
    def __init__(self, processed: _Optional[str] = ...) -> None: ...

class ApplyOpinion(_message.Message):
    __slots__ = ("action", "cause", "processed")
    ACTION_FIELD_NUMBER: _ClassVar[int]
    CAUSE_FIELD_NUMBER: _ClassVar[int]
    PROCESSED_FIELD_NUMBER: _ClassVar[int]
    action: ApplyActionEnum
    cause: str
    processed: str
    def __init__(
        self,
        action: _Optional[_Union[ApplyActionEnum, str]] = ...,
        cause: _Optional[str] = ...,
        processed: _Optional[str] = ...,
    ) -> None: ...

class CustomOpinion(_message.Message):
    __slots__ = ("name", "object")
    NAME_FIELD_NUMBER: _ClassVar[int]
    OBJECT_FIELD_NUMBER: _ClassVar[int]
    name: str
    object: str
    def __init__(self, name: _Optional[str] = ..., object: _Optional[str] = ...) -> None: ...

class ConsumeResponse(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: ConsumeResponseBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[ConsumeResponseBody, _Mapping]] = ...,
    ) -> None: ...

class ConsumeResponseBody(_message.Message):
    __slots__ = ("status",)
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: _message_pb2.ResponseStatus
    def __init__(self, status: _Optional[_Union[_message_pb2.ResponseStatus, _Mapping]] = ...) -> None: ...
