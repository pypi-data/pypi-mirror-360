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

class RegisterStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SUCCESS: _ClassVar[RegisterStatus]
    REGISTERED: _ClassVar[RegisterStatus]

SUCCESS: RegisterStatus
REGISTERED: RegisterStatus

class ListRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListResponse(_message.Message):
    __slots__ = ("contract",)
    CONTRACT_FIELD_NUMBER: _ClassVar[int]
    contract: _containers.RepeatedCompositeFieldContainer[Contract]
    def __init__(self, contract: _Optional[_Iterable[_Union[Contract, _Mapping]]] = ...) -> None: ...

class ExitRequest(_message.Message):
    __slots__ = ("did", "peer", "contract")
    DID_FIELD_NUMBER: _ClassVar[int]
    PEER_FIELD_NUMBER: _ClassVar[int]
    CONTRACT_FIELD_NUMBER: _ClassVar[int]
    did: str
    peer: Peer
    contract: Contract
    def __init__(
        self,
        did: _Optional[str] = ...,
        peer: _Optional[_Union[Peer, _Mapping]] = ...,
        contract: _Optional[_Union[Contract, _Mapping]] = ...,
    ) -> None: ...

class Peer(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class ExitResponse(_message.Message):
    __slots__ = ("status",)
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: str
    def __init__(self, status: _Optional[str] = ...) -> None: ...

class JoinRequest(_message.Message):
    __slots__ = ("did", "peer", "contract")
    DID_FIELD_NUMBER: _ClassVar[int]
    PEER_FIELD_NUMBER: _ClassVar[int]
    CONTRACT_FIELD_NUMBER: _ClassVar[int]
    did: str
    peer: Peer
    contract: Contract
    def __init__(
        self,
        did: _Optional[str] = ...,
        peer: _Optional[_Union[Peer, _Mapping]] = ...,
        contract: _Optional[_Union[Contract, _Mapping]] = ...,
    ) -> None: ...

class JoinResponse(_message.Message):
    __slots__ = ("status", "contract")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    CONTRACT_FIELD_NUMBER: _ClassVar[int]
    status: RegisterStatus
    contract: Contract
    def __init__(
        self,
        status: _Optional[_Union[RegisterStatus, str]] = ...,
        contract: _Optional[_Union[Contract, _Mapping]] = ...,
    ) -> None: ...

class Contract(_message.Message):
    __slots__ = ("address",)
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    address: str
    def __init__(self, address: _Optional[str] = ...) -> None: ...
