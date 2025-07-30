from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Tensor(_message.Message):
    __slots__ = ("offset", "size", "shape", "data_type")
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    SHAPE_FIELD_NUMBER: _ClassVar[int]
    DATA_TYPE_FIELD_NUMBER: _ClassVar[int]
    offset: int
    size: int
    shape: _containers.RepeatedScalarFieldContainer[int]
    data_type: int
    def __init__(self, offset: _Optional[int] = ..., size: _Optional[int] = ..., shape: _Optional[_Iterable[int]] = ..., data_type: _Optional[int] = ...) -> None: ...

class Operator(_message.Message):
    __slots__ = ("op_type", "data")
    OP_TYPE_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    op_type: str
    data: _containers.RepeatedCompositeFieldContainer[Tensor]
    def __init__(self, op_type: _Optional[str] = ..., data: _Optional[_Iterable[_Union[Tensor, _Mapping]]] = ...) -> None: ...

class Layer(_message.Message):
    __slots__ = ("offset", "size", "operators")
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    OPERATORS_FIELD_NUMBER: _ClassVar[int]
    offset: int
    size: int
    operators: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, offset: _Optional[int] = ..., size: _Optional[int] = ..., operators: _Optional[_Iterable[str]] = ...) -> None: ...

class OpMetadata(_message.Message):
    __slots__ = ("max_npu_buffer_size", "first", "last")
    MAX_NPU_BUFFER_SIZE_FIELD_NUMBER: _ClassVar[int]
    FIRST_FIELD_NUMBER: _ClassVar[int]
    LAST_FIELD_NUMBER: _ClassVar[int]
    max_npu_buffer_size: int
    first: str
    last: str
    def __init__(self, max_npu_buffer_size: _Optional[int] = ..., first: _Optional[str] = ..., last: _Optional[str] = ...) -> None: ...

class ExternalData(_message.Message):
    __slots__ = ("filename", "npu", "gpu")
    FILENAME_FIELD_NUMBER: _ClassVar[int]
    NPU_FIELD_NUMBER: _ClassVar[int]
    GPU_FIELD_NUMBER: _ClassVar[int]
    filename: str
    npu: bool
    gpu: bool
    def __init__(self, filename: _Optional[str] = ..., npu: bool = ..., gpu: bool = ...) -> None: ...

class Header(_message.Message):
    __slots__ = ("operators", "op_metadata", "layers", "external_data")
    class OperatorsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: Operator
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[Operator, _Mapping]] = ...) -> None: ...
    class OpMetadataEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: OpMetadata
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[OpMetadata, _Mapping]] = ...) -> None: ...
    OPERATORS_FIELD_NUMBER: _ClassVar[int]
    OP_METADATA_FIELD_NUMBER: _ClassVar[int]
    LAYERS_FIELD_NUMBER: _ClassVar[int]
    EXTERNAL_DATA_FIELD_NUMBER: _ClassVar[int]
    operators: _containers.MessageMap[str, Operator]
    op_metadata: _containers.MessageMap[str, OpMetadata]
    layers: _containers.RepeatedCompositeFieldContainer[Layer]
    external_data: ExternalData
    def __init__(self, operators: _Optional[_Mapping[str, Operator]] = ..., op_metadata: _Optional[_Mapping[str, OpMetadata]] = ..., layers: _Optional[_Iterable[_Union[Layer, _Mapping]]] = ..., external_data: _Optional[_Union[ExternalData, _Mapping]] = ...) -> None: ...
