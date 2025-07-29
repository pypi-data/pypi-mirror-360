from t2iapi.activation_state import types_pb2 as _types_pb2
from t2iapi.metric import types_pb2 as _types_pb2_1
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SetMetricQualityValidityRequest(_message.Message):
    __slots__ = ("handle", "validity")
    HANDLE_FIELD_NUMBER: _ClassVar[int]
    VALIDITY_FIELD_NUMBER: _ClassVar[int]
    handle: str
    validity: _types_pb2_1.MeasurementValidity
    def __init__(self, handle: _Optional[str] = ..., validity: _Optional[_Union[_types_pb2_1.MeasurementValidity, str]] = ...) -> None: ...

class SetMetricValuesWithQualityModeRequest(_message.Message):
    __slots__ = ("handle", "mode")
    HANDLE_FIELD_NUMBER: _ClassVar[int]
    MODE_FIELD_NUMBER: _ClassVar[int]
    handle: str
    mode: _types_pb2_1.GenerationMode
    def __init__(self, handle: _Optional[str] = ..., mode: _Optional[_Union[_types_pb2_1.GenerationMode, str]] = ...) -> None: ...

class SetMetricValuesInRangeRequest(_message.Message):
    __slots__ = ("handle", "lower", "upper")
    HANDLE_FIELD_NUMBER: _ClassVar[int]
    LOWER_FIELD_NUMBER: _ClassVar[int]
    UPPER_FIELD_NUMBER: _ClassVar[int]
    handle: str
    lower: str
    upper: str
    def __init__(self, handle: _Optional[str] = ..., lower: _Optional[str] = ..., upper: _Optional[str] = ...) -> None: ...

class SetMetricStatusRequest(_message.Message):
    __slots__ = ("handle", "status")
    HANDLE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    handle: str
    status: _types_pb2_1.MetricStatus
    def __init__(self, handle: _Optional[str] = ..., status: _Optional[_Union[_types_pb2_1.MetricStatus, str]] = ...) -> None: ...

class SetActivationStateAndUserConfirmableValueRequest(_message.Message):
    __slots__ = ("handle", "activation")
    HANDLE_FIELD_NUMBER: _ClassVar[int]
    ACTIVATION_FIELD_NUMBER: _ClassVar[int]
    handle: str
    activation: _types_pb2.ComponentActivation
    def __init__(self, handle: _Optional[str] = ..., activation: _Optional[_Union[_types_pb2.ComponentActivation, str]] = ...) -> None: ...
