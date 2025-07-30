from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TxInput(_message.Message):
    __slots__ = ("txid", "scriptSig", "sequence", "coinbase", "txinwitness")
    TXID_FIELD_NUMBER: _ClassVar[int]
    SCRIPTSIG_FIELD_NUMBER: _ClassVar[int]
    SEQUENCE_FIELD_NUMBER: _ClassVar[int]
    COINBASE_FIELD_NUMBER: _ClassVar[int]
    TXINWITNESS_FIELD_NUMBER: _ClassVar[int]
    txid: bytes
    scriptSig: bytes
    sequence: int
    coinbase: bytes
    txinwitness: _containers.RepeatedScalarFieldContainer[bytes]
    def __init__(self, txid: _Optional[bytes] = ..., scriptSig: _Optional[bytes] = ..., sequence: _Optional[int] = ..., coinbase: _Optional[bytes] = ..., txinwitness: _Optional[_Iterable[bytes]] = ...) -> None: ...

class TxOutput(_message.Message):
    __slots__ = ("value", "scriptPubKey")
    VALUE_FIELD_NUMBER: _ClassVar[int]
    SCRIPTPUBKEY_FIELD_NUMBER: _ClassVar[int]
    value: int
    scriptPubKey: ScriptPubKey
    def __init__(self, value: _Optional[int] = ..., scriptPubKey: _Optional[_Union[ScriptPubKey, _Mapping]] = ...) -> None: ...

class ScriptPubKey(_message.Message):
    __slots__ = ("asm", "hex", "type", "address")
    ASM_FIELD_NUMBER: _ClassVar[int]
    HEX_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    asm: bytes
    hex: bytes
    type: bytes
    address: bytes
    def __init__(self, asm: _Optional[bytes] = ..., hex: _Optional[bytes] = ..., type: _Optional[bytes] = ..., address: _Optional[bytes] = ...) -> None: ...

class Transaction(_message.Message):
    __slots__ = ("version", "vin", "vout", "locktime", "hash", "blockhash", "time")
    VERSION_FIELD_NUMBER: _ClassVar[int]
    VIN_FIELD_NUMBER: _ClassVar[int]
    VOUT_FIELD_NUMBER: _ClassVar[int]
    LOCKTIME_FIELD_NUMBER: _ClassVar[int]
    HASH_FIELD_NUMBER: _ClassVar[int]
    BLOCKHASH_FIELD_NUMBER: _ClassVar[int]
    TIME_FIELD_NUMBER: _ClassVar[int]
    version: int
    vin: _containers.RepeatedCompositeFieldContainer[TxInput]
    vout: _containers.RepeatedCompositeFieldContainer[TxOutput]
    locktime: int
    hash: bytes
    blockhash: bytes
    time: int
    def __init__(self, version: _Optional[int] = ..., vin: _Optional[_Iterable[_Union[TxInput, _Mapping]]] = ..., vout: _Optional[_Iterable[_Union[TxOutput, _Mapping]]] = ..., locktime: _Optional[int] = ..., hash: _Optional[bytes] = ..., blockhash: _Optional[bytes] = ..., time: _Optional[int] = ...) -> None: ...

class Block(_message.Message):
    __slots__ = ("version", "previousblockhash", "merkleroot", "time", "bits", "nonce", "tx")
    VERSION_FIELD_NUMBER: _ClassVar[int]
    PREVIOUSBLOCKHASH_FIELD_NUMBER: _ClassVar[int]
    MERKLEROOT_FIELD_NUMBER: _ClassVar[int]
    TIME_FIELD_NUMBER: _ClassVar[int]
    BITS_FIELD_NUMBER: _ClassVar[int]
    NONCE_FIELD_NUMBER: _ClassVar[int]
    TX_FIELD_NUMBER: _ClassVar[int]
    version: int
    previousblockhash: bytes
    merkleroot: bytes
    time: int
    bits: int
    nonce: int
    tx: _containers.RepeatedCompositeFieldContainer[Transaction]
    def __init__(self, version: _Optional[int] = ..., previousblockhash: _Optional[bytes] = ..., merkleroot: _Optional[bytes] = ..., time: _Optional[int] = ..., bits: _Optional[int] = ..., nonce: _Optional[int] = ..., tx: _Optional[_Iterable[_Union[Transaction, _Mapping]]] = ...) -> None: ...
