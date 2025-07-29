from t2iapi.context import types_pb2 as _types_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SetLocationDetailRequest(_message.Message):
    __slots__ = ("location",)
    LOCATION_FIELD_NUMBER: _ClassVar[int]
    location: _types_pb2.LocationDetail
    def __init__(self, location: _Optional[_Union[_types_pb2.LocationDetail, _Mapping]] = ...) -> None: ...

class SetContextStateAssociationRequest(_message.Message):
    __slots__ = ("descriptor_handle", "context_state_handle", "context_association")
    DESCRIPTOR_HANDLE_FIELD_NUMBER: _ClassVar[int]
    CONTEXT_STATE_HANDLE_FIELD_NUMBER: _ClassVar[int]
    CONTEXT_ASSOCIATION_FIELD_NUMBER: _ClassVar[int]
    descriptor_handle: str
    context_state_handle: str
    context_association: _types_pb2.ContextAssociation
    def __init__(self, descriptor_handle: _Optional[str] = ..., context_state_handle: _Optional[str] = ..., context_association: _Optional[_Union[_types_pb2.ContextAssociation, str]] = ...) -> None: ...

class CreateContextStateWithAssociationRequest(_message.Message):
    __slots__ = ("descriptor_handle", "context_association")
    DESCRIPTOR_HANDLE_FIELD_NUMBER: _ClassVar[int]
    CONTEXT_ASSOCIATION_FIELD_NUMBER: _ClassVar[int]
    descriptor_handle: str
    context_association: _types_pb2.ContextAssociation
    def __init__(self, descriptor_handle: _Optional[str] = ..., context_association: _Optional[_Union[_types_pb2.ContextAssociation, str]] = ...) -> None: ...

class CreateContextStateWithAssociationAndValidatorsRequest(_message.Message):
    __slots__ = ("descriptor_handle", "context_association", "num_validators")
    DESCRIPTOR_HANDLE_FIELD_NUMBER: _ClassVar[int]
    CONTEXT_ASSOCIATION_FIELD_NUMBER: _ClassVar[int]
    NUM_VALIDATORS_FIELD_NUMBER: _ClassVar[int]
    descriptor_handle: str
    context_association: _types_pb2.ContextAssociation
    num_validators: str
    def __init__(self, descriptor_handle: _Optional[str] = ..., context_association: _Optional[_Union[_types_pb2.ContextAssociation, str]] = ..., num_validators: _Optional[str] = ...) -> None: ...

class CreateContextStateWithAssocAndSpecificValidatorRequest(_message.Message):
    __slots__ = ("descriptor_handle", "context_association", "validator_type")
    DESCRIPTOR_HANDLE_FIELD_NUMBER: _ClassVar[int]
    CONTEXT_ASSOCIATION_FIELD_NUMBER: _ClassVar[int]
    VALIDATOR_TYPE_FIELD_NUMBER: _ClassVar[int]
    descriptor_handle: str
    context_association: _types_pb2.ContextAssociation
    validator_type: _types_pb2.ValidatorType
    def __init__(self, descriptor_handle: _Optional[str] = ..., context_association: _Optional[_Union[_types_pb2.ContextAssociation, str]] = ..., validator_type: _Optional[_Union[_types_pb2.ValidatorType, str]] = ...) -> None: ...

class AssociatePatientRequest(_message.Message):
    __slots__ = ("patient_type",)
    PATIENT_TYPE_FIELD_NUMBER: _ClassVar[int]
    patient_type: _types_pb2.PatientType
    def __init__(self, patient_type: _Optional[_Union[_types_pb2.PatientType, str]] = ...) -> None: ...

class EnsembleIdRequest(_message.Message):
    __slots__ = ("descriptor_handle", "ensemble_id")
    DESCRIPTOR_HANDLE_FIELD_NUMBER: _ClassVar[int]
    ENSEMBLE_ID_FIELD_NUMBER: _ClassVar[int]
    descriptor_handle: str
    ensemble_id: str
    def __init__(self, descriptor_handle: _Optional[str] = ..., ensemble_id: _Optional[str] = ...) -> None: ...

class CreateContextStateWithAssocAndBindingMdibVersionRequest(_message.Message):
    __slots__ = ("descriptor_handle", "context_association")
    DESCRIPTOR_HANDLE_FIELD_NUMBER: _ClassVar[int]
    CONTEXT_ASSOCIATION_FIELD_NUMBER: _ClassVar[int]
    descriptor_handle: str
    context_association: _types_pb2.ContextAssociation
    def __init__(self, descriptor_handle: _Optional[str] = ..., context_association: _Optional[_Union[_types_pb2.ContextAssociation, str]] = ...) -> None: ...

class CreateContextStateWithAssocAndUnbindingMdibVersionRequest(_message.Message):
    __slots__ = ("descriptor_handle", "context_association")
    DESCRIPTOR_HANDLE_FIELD_NUMBER: _ClassVar[int]
    CONTEXT_ASSOCIATION_FIELD_NUMBER: _ClassVar[int]
    descriptor_handle: str
    context_association: _types_pb2.ContextAssociation
    def __init__(self, descriptor_handle: _Optional[str] = ..., context_association: _Optional[_Union[_types_pb2.ContextAssociation, str]] = ...) -> None: ...
