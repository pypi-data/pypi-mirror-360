from google.protobuf import field_mask_pb2 as _field_mask_pb2
from utxorpc.v1alpha.cardano import cardano_pb2 as _cardano_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Stage(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    STAGE_UNSPECIFIED: _ClassVar[Stage]
    STAGE_ACKNOWLEDGED: _ClassVar[Stage]
    STAGE_MEMPOOL: _ClassVar[Stage]
    STAGE_NETWORK: _ClassVar[Stage]
    STAGE_CONFIRMED: _ClassVar[Stage]
STAGE_UNSPECIFIED: Stage
STAGE_ACKNOWLEDGED: Stage
STAGE_MEMPOOL: Stage
STAGE_NETWORK: Stage
STAGE_CONFIRMED: Stage

class AnyChainTx(_message.Message):
    __slots__ = ("raw",)
    RAW_FIELD_NUMBER: _ClassVar[int]
    raw: bytes
    def __init__(self, raw: _Optional[bytes] = ...) -> None: ...

class EvalTxRequest(_message.Message):
    __slots__ = ("tx",)
    TX_FIELD_NUMBER: _ClassVar[int]
    tx: _containers.RepeatedCompositeFieldContainer[AnyChainTx]
    def __init__(self, tx: _Optional[_Iterable[_Union[AnyChainTx, _Mapping]]] = ...) -> None: ...

class AnyChainEval(_message.Message):
    __slots__ = ("cardano",)
    CARDANO_FIELD_NUMBER: _ClassVar[int]
    cardano: _cardano_pb2.TxEval
    def __init__(self, cardano: _Optional[_Union[_cardano_pb2.TxEval, _Mapping]] = ...) -> None: ...

class EvalTxResponse(_message.Message):
    __slots__ = ("report",)
    REPORT_FIELD_NUMBER: _ClassVar[int]
    report: _containers.RepeatedCompositeFieldContainer[AnyChainEval]
    def __init__(self, report: _Optional[_Iterable[_Union[AnyChainEval, _Mapping]]] = ...) -> None: ...

class SubmitTxRequest(_message.Message):
    __slots__ = ("tx",)
    TX_FIELD_NUMBER: _ClassVar[int]
    tx: _containers.RepeatedCompositeFieldContainer[AnyChainTx]
    def __init__(self, tx: _Optional[_Iterable[_Union[AnyChainTx, _Mapping]]] = ...) -> None: ...

class SubmitTxResponse(_message.Message):
    __slots__ = ("ref",)
    REF_FIELD_NUMBER: _ClassVar[int]
    ref: _containers.RepeatedScalarFieldContainer[bytes]
    def __init__(self, ref: _Optional[_Iterable[bytes]] = ...) -> None: ...

class TxInMempool(_message.Message):
    __slots__ = ("ref", "native_bytes", "stage", "cardano")
    REF_FIELD_NUMBER: _ClassVar[int]
    NATIVE_BYTES_FIELD_NUMBER: _ClassVar[int]
    STAGE_FIELD_NUMBER: _ClassVar[int]
    CARDANO_FIELD_NUMBER: _ClassVar[int]
    ref: bytes
    native_bytes: bytes
    stage: Stage
    cardano: _cardano_pb2.Tx
    def __init__(self, ref: _Optional[bytes] = ..., native_bytes: _Optional[bytes] = ..., stage: _Optional[_Union[Stage, str]] = ..., cardano: _Optional[_Union[_cardano_pb2.Tx, _Mapping]] = ...) -> None: ...

class ReadMempoolRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ReadMempoolResponse(_message.Message):
    __slots__ = ("items",)
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    items: _containers.RepeatedCompositeFieldContainer[TxInMempool]
    def __init__(self, items: _Optional[_Iterable[_Union[TxInMempool, _Mapping]]] = ...) -> None: ...

class WaitForTxRequest(_message.Message):
    __slots__ = ("ref",)
    REF_FIELD_NUMBER: _ClassVar[int]
    ref: _containers.RepeatedScalarFieldContainer[bytes]
    def __init__(self, ref: _Optional[_Iterable[bytes]] = ...) -> None: ...

class WaitForTxResponse(_message.Message):
    __slots__ = ("ref", "stage")
    REF_FIELD_NUMBER: _ClassVar[int]
    STAGE_FIELD_NUMBER: _ClassVar[int]
    ref: bytes
    stage: Stage
    def __init__(self, ref: _Optional[bytes] = ..., stage: _Optional[_Union[Stage, str]] = ...) -> None: ...

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

class WatchMempoolRequest(_message.Message):
    __slots__ = ("predicate", "field_mask")
    PREDICATE_FIELD_NUMBER: _ClassVar[int]
    FIELD_MASK_FIELD_NUMBER: _ClassVar[int]
    predicate: TxPredicate
    field_mask: _field_mask_pb2.FieldMask
    def __init__(self, predicate: _Optional[_Union[TxPredicate, _Mapping]] = ..., field_mask: _Optional[_Union[_field_mask_pb2.FieldMask, _Mapping]] = ...) -> None: ...

class WatchMempoolResponse(_message.Message):
    __slots__ = ("tx",)
    TX_FIELD_NUMBER: _ClassVar[int]
    tx: TxInMempool
    def __init__(self, tx: _Optional[_Union[TxInMempool, _Mapping]] = ...) -> None: ...
