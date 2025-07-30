from google.protobuf import field_mask_pb2 as _field_mask_pb2
from utxorpc.v1alpha.cardano import cardano_pb2 as _cardano_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class BlockRef(_message.Message):
    __slots__ = ("slot", "hash", "height")
    SLOT_FIELD_NUMBER: _ClassVar[int]
    HASH_FIELD_NUMBER: _ClassVar[int]
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    slot: int
    hash: bytes
    height: int
    def __init__(self, slot: _Optional[int] = ..., hash: _Optional[bytes] = ..., height: _Optional[int] = ...) -> None: ...

class AnyChainBlock(_message.Message):
    __slots__ = ("native_bytes", "cardano")
    NATIVE_BYTES_FIELD_NUMBER: _ClassVar[int]
    CARDANO_FIELD_NUMBER: _ClassVar[int]
    native_bytes: bytes
    cardano: _cardano_pb2.Block
    def __init__(self, native_bytes: _Optional[bytes] = ..., cardano: _Optional[_Union[_cardano_pb2.Block, _Mapping]] = ...) -> None: ...

class AnyChainTxPattern(_message.Message):
    __slots__ = ("cardano",)
    CARDANO_FIELD_NUMBER: _ClassVar[int]
    cardano: _cardano_pb2.TxPattern
    def __init__(self, cardano: _Optional[_Union[_cardano_pb2.TxPattern, _Mapping]] = ...) -> None: ...

class TxPredicate(_message.Message):
    __slots__ = ("match", "all_of", "any_of")
    MATCH_FIELD_NUMBER: _ClassVar[int]
    NOT_FIELD_NUMBER: _ClassVar[int]
    ALL_OF_FIELD_NUMBER: _ClassVar[int]
    ANY_OF_FIELD_NUMBER: _ClassVar[int]
    match: AnyChainTxPattern
    all_of: _containers.RepeatedCompositeFieldContainer[TxPredicate]
    any_of: _containers.RepeatedCompositeFieldContainer[TxPredicate]
    def __init__(self, match: _Optional[_Union[AnyChainTxPattern, _Mapping]] = ..., all_of: _Optional[_Iterable[_Union[TxPredicate, _Mapping]]] = ..., any_of: _Optional[_Iterable[_Union[TxPredicate, _Mapping]]] = ..., **kwargs) -> None: ...

class WatchTxRequest(_message.Message):
    __slots__ = ("predicate", "field_mask", "intersect")
    PREDICATE_FIELD_NUMBER: _ClassVar[int]
    FIELD_MASK_FIELD_NUMBER: _ClassVar[int]
    INTERSECT_FIELD_NUMBER: _ClassVar[int]
    predicate: TxPredicate
    field_mask: _field_mask_pb2.FieldMask
    intersect: _containers.RepeatedCompositeFieldContainer[BlockRef]
    def __init__(self, predicate: _Optional[_Union[TxPredicate, _Mapping]] = ..., field_mask: _Optional[_Union[_field_mask_pb2.FieldMask, _Mapping]] = ..., intersect: _Optional[_Iterable[_Union[BlockRef, _Mapping]]] = ...) -> None: ...

class AnyChainTx(_message.Message):
    __slots__ = ("cardano", "block")
    CARDANO_FIELD_NUMBER: _ClassVar[int]
    BLOCK_FIELD_NUMBER: _ClassVar[int]
    cardano: _cardano_pb2.Tx
    block: AnyChainBlock
    def __init__(self, cardano: _Optional[_Union[_cardano_pb2.Tx, _Mapping]] = ..., block: _Optional[_Union[AnyChainBlock, _Mapping]] = ...) -> None: ...

class WatchTxResponse(_message.Message):
    __slots__ = ("apply", "undo")
    APPLY_FIELD_NUMBER: _ClassVar[int]
    UNDO_FIELD_NUMBER: _ClassVar[int]
    apply: AnyChainTx
    undo: AnyChainTx
    def __init__(self, apply: _Optional[_Union[AnyChainTx, _Mapping]] = ..., undo: _Optional[_Union[AnyChainTx, _Mapping]] = ...) -> None: ...
