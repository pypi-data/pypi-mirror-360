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

class CreateAddressRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class CreateAddressResponse(_message.Message):
    __slots__ = ("address",)
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    address: str
    def __init__(self, address: _Optional[str] = ...) -> None: ...

class TransactionRequest(_message.Message):
    __slots__ = ("toAddress", "points", "metadata")
    TOADDRESS_FIELD_NUMBER: _ClassVar[int]
    POINTS_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    toAddress: str
    points: int
    metadata: str
    def __init__(
        self, toAddress: _Optional[str] = ..., points: _Optional[int] = ..., metadata: _Optional[str] = ...
    ) -> None: ...

class TransactionResponse(_message.Message):
    __slots__ = ("transaction_id",)
    TRANSACTION_ID_FIELD_NUMBER: _ClassVar[int]
    transaction_id: int
    def __init__(self, transaction_id: _Optional[int] = ...) -> None: ...

class BalanceRequest(_message.Message):
    __slots__ = ("address",)
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    address: str
    def __init__(self, address: _Optional[str] = ...) -> None: ...

class BalanceResponse(_message.Message):
    __slots__ = ("total", "available")
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    AVAILABLE_FIELD_NUMBER: _ClassVar[int]
    total: int
    available: int
    def __init__(self, total: _Optional[int] = ..., available: _Optional[int] = ...) -> None: ...

class WalletInfoRequest(_message.Message):
    __slots__ = ("address",)
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    address: str
    def __init__(self, address: _Optional[str] = ...) -> None: ...

class WalletInfoResponse(_message.Message):
    __slots__ = ("total", "available", "transactions")
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    AVAILABLE_FIELD_NUMBER: _ClassVar[int]
    TRANSACTIONS_FIELD_NUMBER: _ClassVar[int]
    total: int
    available: int
    transactions: _containers.RepeatedCompositeFieldContainer[Transaction]
    def __init__(
        self,
        total: _Optional[int] = ...,
        available: _Optional[int] = ...,
        transactions: _Optional[_Iterable[_Union[Transaction, _Mapping]]] = ...,
    ) -> None: ...

class Transaction(_message.Message):
    __slots__ = ("to_address", "points", "metadata")
    TO_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    POINTS_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    to_address: str
    points: int
    metadata: str
    def __init__(
        self, to_address: _Optional[str] = ..., points: _Optional[int] = ..., metadata: _Optional[str] = ...
    ) -> None: ...
