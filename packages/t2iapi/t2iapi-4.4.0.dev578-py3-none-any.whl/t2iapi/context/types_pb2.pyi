from google.protobuf import wrappers_pb2 as _wrappers_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ContextAssociation(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    CONTEXT_ASSOCIATION_NOT_ASSOCIATED: _ClassVar[ContextAssociation]
    CONTEXT_ASSOCIATION_PRE_ASSOCIATED: _ClassVar[ContextAssociation]
    CONTEXT_ASSOCIATION_ASSOCIATED: _ClassVar[ContextAssociation]
    CONTEXT_ASSOCIATION_DISASSOCIATED: _ClassVar[ContextAssociation]

class PatientType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    PATIENT_TYPE_UNSPECIFIED: _ClassVar[PatientType]
    PATIENT_TYPE_ADULT: _ClassVar[PatientType]
    PATIENT_TYPE_ADOLESCENT: _ClassVar[PatientType]
    PATIENT_TYPE_PEDIATRIC: _ClassVar[PatientType]
    PATIENT_TYPE_INFANT: _ClassVar[PatientType]
    PATIENT_TYPE_NEONATAL: _ClassVar[PatientType]
    PATIENT_TYPE_OTHER: _ClassVar[PatientType]

class ValidatorType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    VALIDATOR_TYPE_USER: _ClassVar[ValidatorType]
    VALIDATOR_TYPE_CLINICAL_SUPER_USER: _ClassVar[ValidatorType]
    VALIDATOR_TYPE_BIOMED: _ClassVar[ValidatorType]
    VALIDATOR_TYPE_SERVICE_PERSONNEL: _ClassVar[ValidatorType]
    VALIDATOR_TYPE_REMOTE_SERVICE_OPERATION: _ClassVar[ValidatorType]
    VALIDATOR_TYPE_TECHNICAL_MEANS: _ClassVar[ValidatorType]
CONTEXT_ASSOCIATION_NOT_ASSOCIATED: ContextAssociation
CONTEXT_ASSOCIATION_PRE_ASSOCIATED: ContextAssociation
CONTEXT_ASSOCIATION_ASSOCIATED: ContextAssociation
CONTEXT_ASSOCIATION_DISASSOCIATED: ContextAssociation
PATIENT_TYPE_UNSPECIFIED: PatientType
PATIENT_TYPE_ADULT: PatientType
PATIENT_TYPE_ADOLESCENT: PatientType
PATIENT_TYPE_PEDIATRIC: PatientType
PATIENT_TYPE_INFANT: PatientType
PATIENT_TYPE_NEONATAL: PatientType
PATIENT_TYPE_OTHER: PatientType
VALIDATOR_TYPE_USER: ValidatorType
VALIDATOR_TYPE_CLINICAL_SUPER_USER: ValidatorType
VALIDATOR_TYPE_BIOMED: ValidatorType
VALIDATOR_TYPE_SERVICE_PERSONNEL: ValidatorType
VALIDATOR_TYPE_REMOTE_SERVICE_OPERATION: ValidatorType
VALIDATOR_TYPE_TECHNICAL_MEANS: ValidatorType

class LocationDetail(_message.Message):
    __slots__ = ("poc", "room", "bed", "facility", "building", "floor")
    POC_FIELD_NUMBER: _ClassVar[int]
    ROOM_FIELD_NUMBER: _ClassVar[int]
    BED_FIELD_NUMBER: _ClassVar[int]
    FACILITY_FIELD_NUMBER: _ClassVar[int]
    BUILDING_FIELD_NUMBER: _ClassVar[int]
    FLOOR_FIELD_NUMBER: _ClassVar[int]
    poc: _wrappers_pb2.StringValue
    room: _wrappers_pb2.StringValue
    bed: _wrappers_pb2.StringValue
    facility: _wrappers_pb2.StringValue
    building: _wrappers_pb2.StringValue
    floor: _wrappers_pb2.StringValue
    def __init__(self, poc: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., room: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., bed: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., facility: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., building: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., floor: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ...) -> None: ...
