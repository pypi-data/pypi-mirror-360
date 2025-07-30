from t2iapi.operation import types_pb2 as _types_pb2
from google.protobuf import duration_pb2 as _duration_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SetOperatingModeRequest(_message.Message):
    __slots__ = ("handle", "operating_mode")
    HANDLE_FIELD_NUMBER: _ClassVar[int]
    OPERATING_MODE_FIELD_NUMBER: _ClassVar[int]
    handle: str
    operating_mode: _types_pb2.OperatingMode
    def __init__(self, handle: _Optional[str] = ..., operating_mode: _Optional[_Union[_types_pb2.OperatingMode, str]] = ...) -> None: ...

class SetInvocationEffectiveTimeoutLessThanOrEqualToThresholdRequest(_message.Message):
    __slots__ = ("handle", "threshold")
    HANDLE_FIELD_NUMBER: _ClassVar[int]
    THRESHOLD_FIELD_NUMBER: _ClassVar[int]
    handle: str
    threshold: _duration_pb2.Duration
    def __init__(self, handle: _Optional[str] = ..., threshold: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ...) -> None: ...
