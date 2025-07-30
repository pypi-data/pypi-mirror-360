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

class FetchBlockRequest(_message.Message):
    __slots__ = ("ref", "field_mask")
    REF_FIELD_NUMBER: _ClassVar[int]
    FIELD_MASK_FIELD_NUMBER: _ClassVar[int]
    ref: _containers.RepeatedCompositeFieldContainer[BlockRef]
    field_mask: _field_mask_pb2.FieldMask
    def __init__(self, ref: _Optional[_Iterable[_Union[BlockRef, _Mapping]]] = ..., field_mask: _Optional[_Union[_field_mask_pb2.FieldMask, _Mapping]] = ...) -> None: ...

class FetchBlockResponse(_message.Message):
    __slots__ = ("block",)
    BLOCK_FIELD_NUMBER: _ClassVar[int]
    block: _containers.RepeatedCompositeFieldContainer[AnyChainBlock]
    def __init__(self, block: _Optional[_Iterable[_Union[AnyChainBlock, _Mapping]]] = ...) -> None: ...

class DumpHistoryRequest(_message.Message):
    __slots__ = ("start_token", "max_items", "field_mask")
    START_TOKEN_FIELD_NUMBER: _ClassVar[int]
    MAX_ITEMS_FIELD_NUMBER: _ClassVar[int]
    FIELD_MASK_FIELD_NUMBER: _ClassVar[int]
    start_token: BlockRef
    max_items: int
    field_mask: _field_mask_pb2.FieldMask
    def __init__(self, start_token: _Optional[_Union[BlockRef, _Mapping]] = ..., max_items: _Optional[int] = ..., field_mask: _Optional[_Union[_field_mask_pb2.FieldMask, _Mapping]] = ...) -> None: ...

class DumpHistoryResponse(_message.Message):
    __slots__ = ("block", "next_token")
    BLOCK_FIELD_NUMBER: _ClassVar[int]
    NEXT_TOKEN_FIELD_NUMBER: _ClassVar[int]
    block: _containers.RepeatedCompositeFieldContainer[AnyChainBlock]
    next_token: BlockRef
    def __init__(self, block: _Optional[_Iterable[_Union[AnyChainBlock, _Mapping]]] = ..., next_token: _Optional[_Union[BlockRef, _Mapping]] = ...) -> None: ...

class FollowTipRequest(_message.Message):
    __slots__ = ("intersect", "field_mask")
    INTERSECT_FIELD_NUMBER: _ClassVar[int]
    FIELD_MASK_FIELD_NUMBER: _ClassVar[int]
    intersect: _containers.RepeatedCompositeFieldContainer[BlockRef]
    field_mask: _field_mask_pb2.FieldMask
    def __init__(self, intersect: _Optional[_Iterable[_Union[BlockRef, _Mapping]]] = ..., field_mask: _Optional[_Union[_field_mask_pb2.FieldMask, _Mapping]] = ...) -> None: ...

class FollowTipResponse(_message.Message):
    __slots__ = ("apply", "undo", "reset")
    APPLY_FIELD_NUMBER: _ClassVar[int]
    UNDO_FIELD_NUMBER: _ClassVar[int]
    RESET_FIELD_NUMBER: _ClassVar[int]
    apply: AnyChainBlock
    undo: AnyChainBlock
    reset: BlockRef
    def __init__(self, apply: _Optional[_Union[AnyChainBlock, _Mapping]] = ..., undo: _Optional[_Union[AnyChainBlock, _Mapping]] = ..., reset: _Optional[_Union[BlockRef, _Mapping]] = ...) -> None: ...

class ReadTipRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ReadTipResponse(_message.Message):
    __slots__ = ("tip", "timestamp")
    TIP_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    tip: BlockRef
    timestamp: int
    def __init__(self, tip: _Optional[_Union[BlockRef, _Mapping]] = ..., timestamp: _Optional[int] = ...) -> None: ...
