from t2iapi.alert import types_pb2 as _types_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SetAlertConditionPresenceRequest(_message.Message):
    __slots__ = ("handle", "presence")
    HANDLE_FIELD_NUMBER: _ClassVar[int]
    PRESENCE_FIELD_NUMBER: _ClassVar[int]
    handle: str
    presence: bool
    def __init__(self, handle: _Optional[str] = ..., presence: bool = ...) -> None: ...

class SetAlarmSignalInactivationStateRequest(_message.Message):
    __slots__ = ("handle", "enable")
    HANDLE_FIELD_NUMBER: _ClassVar[int]
    ENABLE_FIELD_NUMBER: _ClassVar[int]
    handle: str
    enable: bool
    def __init__(self, handle: _Optional[str] = ..., enable: bool = ...) -> None: ...

class SetSomeAlertSignalPresenceRequest(_message.Message):
    __slots__ = ("handle", "min_subset_size", "presence")
    HANDLE_FIELD_NUMBER: _ClassVar[int]
    MIN_SUBSET_SIZE_FIELD_NUMBER: _ClassVar[int]
    PRESENCE_FIELD_NUMBER: _ClassVar[int]
    handle: _containers.RepeatedScalarFieldContainer[str]
    min_subset_size: int
    presence: _containers.RepeatedScalarFieldContainer[_types_pb2.AlertSignalPresence]
    def __init__(self, handle: _Optional[_Iterable[str]] = ..., min_subset_size: _Optional[int] = ..., presence: _Optional[_Iterable[_Union[_types_pb2.AlertSignalPresence, str]]] = ...) -> None: ...
