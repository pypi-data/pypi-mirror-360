from google.protobuf import wrappers_pb2 as _wrappers_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ReportType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    REPORT_TYPE_EPISODIC_ALERT_REPORT: _ClassVar[ReportType]
    REPORT_TYPE_EPISODIC_COMPONENT_REPORT: _ClassVar[ReportType]
    REPORT_TYPE_EPISODIC_CONTEXT_REPORT: _ClassVar[ReportType]
    REPORT_TYPE_EPISODIC_METRIC_REPORT: _ClassVar[ReportType]
    REPORT_TYPE_EPISODIC_OPERATIONAL_STATE_REPORT: _ClassVar[ReportType]
    REPORT_TYPE_PERIODIC_ALERT_REPORT: _ClassVar[ReportType]
    REPORT_TYPE_PERIODIC_COMPONENT_REPORT: _ClassVar[ReportType]
    REPORT_TYPE_PERIODIC_CONTEXT_REPORT: _ClassVar[ReportType]
    REPORT_TYPE_PERIODIC_METRIC_REPORT: _ClassVar[ReportType]
    REPORT_TYPE_PERIODIC_OPERATIONAL_STATE_REPORT: _ClassVar[ReportType]
    REPORT_TYPE_DESCRIPTION_MODIFICATION_REPORT: _ClassVar[ReportType]
    REPORT_TYPE_OPERATION_INVOKED_REPORT: _ClassVar[ReportType]
    REPORT_TYPE_SYSTEM_ERROR_REPORT: _ClassVar[ReportType]
    REPORT_TYPE_OBSERVED_VALUE_STREAM: _ClassVar[ReportType]
    REPORT_TYPE_WAVEFORM_STREAM: _ClassVar[ReportType]

class MdsOperatingMode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    MDS_OPERATING_MODE_NORMAL: _ClassVar[MdsOperatingMode]
    MDS_OPERATING_MODE_DEMO: _ClassVar[MdsOperatingMode]
    MDS_OPERATING_MODE_SERVICE: _ClassVar[MdsOperatingMode]
    MDS_OPERATING_MODE_MAINTENANCE: _ClassVar[MdsOperatingMode]

class DescriptorClass(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    DESCRIPTOR_CLASS_ABSTRACT: _ClassVar[DescriptorClass]
    DESCRIPTOR_CLASS_MDS: _ClassVar[DescriptorClass]

class CalibrationState(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    CALIBRATION_STATE_NOT_CALIBRATED: _ClassVar[CalibrationState]
    CALIBRATION_STATE_CALIBRATION_REQUIRED: _ClassVar[CalibrationState]
    CALIBRATION_STATE_RUNNING: _ClassVar[CalibrationState]
    CALIBRATION_STATE_CALIBRATED: _ClassVar[CalibrationState]
    CALIBRATION_STATE_OTHER: _ClassVar[CalibrationState]
REPORT_TYPE_EPISODIC_ALERT_REPORT: ReportType
REPORT_TYPE_EPISODIC_COMPONENT_REPORT: ReportType
REPORT_TYPE_EPISODIC_CONTEXT_REPORT: ReportType
REPORT_TYPE_EPISODIC_METRIC_REPORT: ReportType
REPORT_TYPE_EPISODIC_OPERATIONAL_STATE_REPORT: ReportType
REPORT_TYPE_PERIODIC_ALERT_REPORT: ReportType
REPORT_TYPE_PERIODIC_COMPONENT_REPORT: ReportType
REPORT_TYPE_PERIODIC_CONTEXT_REPORT: ReportType
REPORT_TYPE_PERIODIC_METRIC_REPORT: ReportType
REPORT_TYPE_PERIODIC_OPERATIONAL_STATE_REPORT: ReportType
REPORT_TYPE_DESCRIPTION_MODIFICATION_REPORT: ReportType
REPORT_TYPE_OPERATION_INVOKED_REPORT: ReportType
REPORT_TYPE_SYSTEM_ERROR_REPORT: ReportType
REPORT_TYPE_OBSERVED_VALUE_STREAM: ReportType
REPORT_TYPE_WAVEFORM_STREAM: ReportType
MDS_OPERATING_MODE_NORMAL: MdsOperatingMode
MDS_OPERATING_MODE_DEMO: MdsOperatingMode
MDS_OPERATING_MODE_SERVICE: MdsOperatingMode
MDS_OPERATING_MODE_MAINTENANCE: MdsOperatingMode
DESCRIPTOR_CLASS_ABSTRACT: DescriptorClass
DESCRIPTOR_CLASS_MDS: DescriptorClass
CALIBRATION_STATE_NOT_CALIBRATED: CalibrationState
CALIBRATION_STATE_CALIBRATION_REQUIRED: CalibrationState
CALIBRATION_STATE_RUNNING: CalibrationState
CALIBRATION_STATE_CALIBRATED: CalibrationState
CALIBRATION_STATE_OTHER: CalibrationState

class ExpandedName(_message.Message):
    __slots__ = ("uri", "local_name")
    URI_FIELD_NUMBER: _ClassVar[int]
    LOCAL_NAME_FIELD_NUMBER: _ClassVar[int]
    uri: _wrappers_pb2.StringValue
    local_name: str
    def __init__(self, uri: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., local_name: _Optional[str] = ...) -> None: ...
