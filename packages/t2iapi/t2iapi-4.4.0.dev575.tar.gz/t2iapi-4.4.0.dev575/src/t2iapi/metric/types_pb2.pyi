from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from typing import ClassVar as _ClassVar

DESCRIPTOR: _descriptor.FileDescriptor

class MeasurementValidity(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    MEASUREMENT_VALIDITY_VALID: _ClassVar[MeasurementValidity]
    MEASUREMENT_VALIDITY_VALIDATED_DATA: _ClassVar[MeasurementValidity]
    MEASUREMENT_VALIDITY_MEASUREMENT_ONGOING: _ClassVar[MeasurementValidity]
    MEASUREMENT_VALIDITY_QUESTIONABLE: _ClassVar[MeasurementValidity]
    MEASUREMENT_VALIDITY_CALIBRATION_ONGOING: _ClassVar[MeasurementValidity]
    MEASUREMENT_VALIDITY_INVALID: _ClassVar[MeasurementValidity]
    MEASUREMENT_VALIDITY_OVERFLOW: _ClassVar[MeasurementValidity]
    MEASUREMENT_VALIDITY_UNDERFLOW: _ClassVar[MeasurementValidity]
    MEASUREMENT_VALIDITY_NA: _ClassVar[MeasurementValidity]

class GenerationMode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    GENERATION_MODE_REAL: _ClassVar[GenerationMode]
    GENERATION_MODE_TEST: _ClassVar[GenerationMode]
    GENERATION_MODE_DEMO: _ClassVar[GenerationMode]

class ModeOfOperation(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    MODE_OF_OPERATION_ON: _ClassVar[ModeOfOperation]
    MODE_OF_OPERATION_OFF: _ClassVar[ModeOfOperation]
    MODE_OF_OPERATION_PAUSED: _ClassVar[ModeOfOperation]

class MetricStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    METRIC_STATUS_PERFORMED_OR_APPLIED: _ClassVar[MetricStatus]
    METRIC_STATUS_CURRENTLY_INITIALIZING: _ClassVar[MetricStatus]
    METRIC_STATUS_INITIALIZED_BUT_NOT_PERFORMING_OR_APPLYING: _ClassVar[MetricStatus]
    METRIC_STATUS_CURRENTLY_DE_INITIALIZING: _ClassVar[MetricStatus]
    METRIC_STATUS_DE_INITIALIZED_AND_NOT_PERFORMING_OR_APPLYING: _ClassVar[MetricStatus]
    METRIC_STATUS_FAILED: _ClassVar[MetricStatus]

class MetricDeterminationMode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    METRIC_DETERMINATION_MODE_EPISODICALLY: _ClassVar[MetricDeterminationMode]
    METRIC_DETERMINATION_MODE_PERIODICALLY: _ClassVar[MetricDeterminationMode]
MEASUREMENT_VALIDITY_VALID: MeasurementValidity
MEASUREMENT_VALIDITY_VALIDATED_DATA: MeasurementValidity
MEASUREMENT_VALIDITY_MEASUREMENT_ONGOING: MeasurementValidity
MEASUREMENT_VALIDITY_QUESTIONABLE: MeasurementValidity
MEASUREMENT_VALIDITY_CALIBRATION_ONGOING: MeasurementValidity
MEASUREMENT_VALIDITY_INVALID: MeasurementValidity
MEASUREMENT_VALIDITY_OVERFLOW: MeasurementValidity
MEASUREMENT_VALIDITY_UNDERFLOW: MeasurementValidity
MEASUREMENT_VALIDITY_NA: MeasurementValidity
GENERATION_MODE_REAL: GenerationMode
GENERATION_MODE_TEST: GenerationMode
GENERATION_MODE_DEMO: GenerationMode
MODE_OF_OPERATION_ON: ModeOfOperation
MODE_OF_OPERATION_OFF: ModeOfOperation
MODE_OF_OPERATION_PAUSED: ModeOfOperation
METRIC_STATUS_PERFORMED_OR_APPLIED: MetricStatus
METRIC_STATUS_CURRENTLY_INITIALIZING: MetricStatus
METRIC_STATUS_INITIALIZED_BUT_NOT_PERFORMING_OR_APPLYING: MetricStatus
METRIC_STATUS_CURRENTLY_DE_INITIALIZING: MetricStatus
METRIC_STATUS_DE_INITIALIZED_AND_NOT_PERFORMING_OR_APPLYING: MetricStatus
METRIC_STATUS_FAILED: MetricStatus
METRIC_DETERMINATION_MODE_EPISODICALLY: MetricDeterminationMode
METRIC_DETERMINATION_MODE_PERIODICALLY: MetricDeterminationMode
