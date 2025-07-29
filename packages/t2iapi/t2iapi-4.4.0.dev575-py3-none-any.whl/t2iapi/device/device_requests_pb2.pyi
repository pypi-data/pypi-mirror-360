from t2iapi.device import types_pb2 as _types_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TriggerReportRequest(_message.Message):
    __slots__ = ("report",)
    REPORT_FIELD_NUMBER: _ClassVar[int]
    report: _types_pb2.ReportType
    def __init__(self, report: _Optional[_Union[_types_pb2.ReportType, str]] = ...) -> None: ...

class SetDeviceOperatingModeRequest(_message.Message):
    __slots__ = ("mode",)
    MODE_FIELD_NUMBER: _ClassVar[int]
    mode: _types_pb2.MdsOperatingMode
    def __init__(self, mode: _Optional[_Union[_types_pb2.MdsOperatingMode, str]] = ...) -> None: ...

class SetMdsOperatingModeRequest(_message.Message):
    __slots__ = ("handle", "mode")
    HANDLE_FIELD_NUMBER: _ClassVar[int]
    MODE_FIELD_NUMBER: _ClassVar[int]
    handle: str
    mode: _types_pb2.MdsOperatingMode
    def __init__(self, handle: _Optional[str] = ..., mode: _Optional[_Union[_types_pb2.MdsOperatingMode, str]] = ...) -> None: ...

class SetLanguageRequest(_message.Message):
    __slots__ = ("language",)
    LANGUAGE_FIELD_NUMBER: _ClassVar[int]
    language: str
    def __init__(self, language: _Optional[str] = ...) -> None: ...

class SetMdsUiLanguageRequest(_message.Message):
    __slots__ = ("handle", "language")
    HANDLE_FIELD_NUMBER: _ClassVar[int]
    LANGUAGE_FIELD_NUMBER: _ClassVar[int]
    handle: str
    language: str
    def __init__(self, handle: _Optional[str] = ..., language: _Optional[str] = ...) -> None: ...

class GetRemovableDescriptorsOfClassRequest(_message.Message):
    __slots__ = ("descriptor_class",)
    DESCRIPTOR_CLASS_FIELD_NUMBER: _ClassVar[int]
    descriptor_class: _types_pb2.DescriptorClass
    def __init__(self, descriptor_class: _Optional[_Union[_types_pb2.DescriptorClass, str]] = ...) -> None: ...

class SetBatteryUsageRequest(_message.Message):
    __slots__ = ("handle", "use")
    HANDLE_FIELD_NUMBER: _ClassVar[int]
    USE_FIELD_NUMBER: _ClassVar[int]
    handle: str
    use: bool
    def __init__(self, handle: _Optional[str] = ..., use: bool = ...) -> None: ...

class TriggerDescriptorUpdateRequest(_message.Message):
    __slots__ = ("handle",)
    HANDLE_FIELD_NUMBER: _ClassVar[int]
    handle: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, handle: _Optional[_Iterable[str]] = ...) -> None: ...

class ProvideInformationAboutLastCalibrationRequest(_message.Message):
    __slots__ = ("handle", "calibration_state")
    HANDLE_FIELD_NUMBER: _ClassVar[int]
    CALIBRATION_STATE_FIELD_NUMBER: _ClassVar[int]
    handle: str
    calibration_state: _types_pb2.CalibrationState
    def __init__(self, handle: _Optional[str] = ..., calibration_state: _Optional[_Union[_types_pb2.CalibrationState, str]] = ...) -> None: ...

class ProvideInformationAboutNextCalibrationRequest(_message.Message):
    __slots__ = ("handle", "calibration_state")
    HANDLE_FIELD_NUMBER: _ClassVar[int]
    CALIBRATION_STATE_FIELD_NUMBER: _ClassVar[int]
    handle: str
    calibration_state: _types_pb2.CalibrationState
    def __init__(self, handle: _Optional[str] = ..., calibration_state: _Optional[_Union[_types_pb2.CalibrationState, str]] = ...) -> None: ...

class InsertContainmentTreeEntryForSequenceIdRequest(_message.Message):
    __slots__ = ("handle", "sequence_id")
    HANDLE_FIELD_NUMBER: _ClassVar[int]
    SEQUENCE_ID_FIELD_NUMBER: _ClassVar[int]
    handle: str
    sequence_id: str
    def __init__(self, handle: _Optional[str] = ..., sequence_id: _Optional[str] = ...) -> None: ...
