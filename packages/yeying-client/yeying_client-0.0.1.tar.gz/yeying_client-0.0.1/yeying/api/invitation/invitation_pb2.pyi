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

class InvitationSceneEnum(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    INVITATION_SCENE_UNKNOWN: _ClassVar[InvitationSceneEnum]
    INVITATION_SCENE_USER: _ClassVar[InvitationSceneEnum]

INVITATION_SCENE_UNKNOWN: InvitationSceneEnum
INVITATION_SCENE_USER: InvitationSceneEnum

class InvitationMetadata(_message.Message):
    __slots__ = ("scene", "code", "createdAt", "expiredAt", "inviter", "invitee", "signature")
    SCENE_FIELD_NUMBER: _ClassVar[int]
    CODE_FIELD_NUMBER: _ClassVar[int]
    CREATEDAT_FIELD_NUMBER: _ClassVar[int]
    EXPIREDAT_FIELD_NUMBER: _ClassVar[int]
    INVITER_FIELD_NUMBER: _ClassVar[int]
    INVITEE_FIELD_NUMBER: _ClassVar[int]
    SIGNATURE_FIELD_NUMBER: _ClassVar[int]
    scene: InvitationSceneEnum
    code: str
    createdAt: str
    expiredAt: str
    inviter: str
    invitee: str
    signature: str
    def __init__(
        self,
        scene: _Optional[_Union[InvitationSceneEnum, str]] = ...,
        code: _Optional[str] = ...,
        createdAt: _Optional[str] = ...,
        expiredAt: _Optional[str] = ...,
        inviter: _Optional[str] = ...,
        invitee: _Optional[str] = ...,
        signature: _Optional[str] = ...,
    ) -> None: ...

class InvitationUseState(_message.Message):
    __slots__ = ("code", "usedAt", "user", "signature")
    CODE_FIELD_NUMBER: _ClassVar[int]
    USEDAT_FIELD_NUMBER: _ClassVar[int]
    USER_FIELD_NUMBER: _ClassVar[int]
    SIGNATURE_FIELD_NUMBER: _ClassVar[int]
    code: str
    usedAt: str
    user: str
    signature: str
    def __init__(
        self,
        code: _Optional[str] = ...,
        usedAt: _Optional[str] = ...,
        user: _Optional[str] = ...,
        signature: _Optional[str] = ...,
    ) -> None: ...

class CreateInvitationRequest(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: CreateInvitationRequestBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[CreateInvitationRequestBody, _Mapping]] = ...,
    ) -> None: ...

class CreateInvitationRequestBody(_message.Message):
    __slots__ = ("invitation",)
    INVITATION_FIELD_NUMBER: _ClassVar[int]
    invitation: InvitationMetadata
    def __init__(self, invitation: _Optional[_Union[InvitationMetadata, _Mapping]] = ...) -> None: ...

class CreateInvitationResponse(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: CreateInvitationResponseBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[CreateInvitationResponseBody, _Mapping]] = ...,
    ) -> None: ...

class CreateInvitationResponseBody(_message.Message):
    __slots__ = ("status", "invitation")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    INVITATION_FIELD_NUMBER: _ClassVar[int]
    status: _message_pb2.ResponseStatus
    invitation: InvitationMetadata
    def __init__(
        self,
        status: _Optional[_Union[_message_pb2.ResponseStatus, _Mapping]] = ...,
        invitation: _Optional[_Union[InvitationMetadata, _Mapping]] = ...,
    ) -> None: ...

class SearchInvitationRequest(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: SearchInvitationRequestBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[SearchInvitationRequestBody, _Mapping]] = ...,
    ) -> None: ...

class SearchInvitationRequestBody(_message.Message):
    __slots__ = ("page",)
    PAGE_FIELD_NUMBER: _ClassVar[int]
    page: _message_pb2.RequestPage
    def __init__(self, page: _Optional[_Union[_message_pb2.RequestPage, _Mapping]] = ...) -> None: ...

class SearchInvitationResponse(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: SearchInvitationResponseBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[SearchInvitationResponseBody, _Mapping]] = ...,
    ) -> None: ...

class SearchInvitationResponseBody(_message.Message):
    __slots__ = ("status", "invitations", "page")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    INVITATIONS_FIELD_NUMBER: _ClassVar[int]
    PAGE_FIELD_NUMBER: _ClassVar[int]
    status: _message_pb2.ResponseStatus
    invitations: _containers.RepeatedCompositeFieldContainer[InvitationMetadata]
    page: _message_pb2.ResponsePage
    def __init__(
        self,
        status: _Optional[_Union[_message_pb2.ResponseStatus, _Mapping]] = ...,
        invitations: _Optional[_Iterable[_Union[InvitationMetadata, _Mapping]]] = ...,
        page: _Optional[_Union[_message_pb2.ResponsePage, _Mapping]] = ...,
    ) -> None: ...

class InvitationDetailRequest(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: InvitationDetailRequestBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[InvitationDetailRequestBody, _Mapping]] = ...,
    ) -> None: ...

class InvitationDetailRequestBody(_message.Message):
    __slots__ = ("code",)
    CODE_FIELD_NUMBER: _ClassVar[int]
    code: str
    def __init__(self, code: _Optional[str] = ...) -> None: ...

class InvitationDetailResponse(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: InvitationDetailResponseBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[InvitationDetailResponseBody, _Mapping]] = ...,
    ) -> None: ...

class InvitationDetailResponseBody(_message.Message):
    __slots__ = ("status", "invitation", "state")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    INVITATION_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    status: _message_pb2.ResponseStatus
    invitation: InvitationMetadata
    state: InvitationUseState
    def __init__(
        self,
        status: _Optional[_Union[_message_pb2.ResponseStatus, _Mapping]] = ...,
        invitation: _Optional[_Union[InvitationMetadata, _Mapping]] = ...,
        state: _Optional[_Union[InvitationUseState, _Mapping]] = ...,
    ) -> None: ...
