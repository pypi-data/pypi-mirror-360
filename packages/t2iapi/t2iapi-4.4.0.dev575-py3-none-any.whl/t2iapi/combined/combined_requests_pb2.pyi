from t2iapi.context import types_pb2 as _types_pb2
from t2iapi.operation import types_pb2 as _types_pb2_1
from t2iapi.activation_state import types_pb2 as _types_pb2_1_1
from t2iapi.metric import types_pb2 as _types_pb2_1_1_1
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CreateContextStateWithAssociationAndSetOperatingModeRequest(_message.Message):
    __slots__ = ("context_descriptor_handle", "context_association", "operation_descriptor_handle", "operating_mode")
    CONTEXT_DESCRIPTOR_HANDLE_FIELD_NUMBER: _ClassVar[int]
    CONTEXT_ASSOCIATION_FIELD_NUMBER: _ClassVar[int]
    OPERATION_DESCRIPTOR_HANDLE_FIELD_NUMBER: _ClassVar[int]
    OPERATING_MODE_FIELD_NUMBER: _ClassVar[int]
    context_descriptor_handle: str
    context_association: _types_pb2.ContextAssociation
    operation_descriptor_handle: str
    operating_mode: _types_pb2_1.OperatingMode
    def __init__(self, context_descriptor_handle: _Optional[str] = ..., context_association: _Optional[_Union[_types_pb2.ContextAssociation, str]] = ..., operation_descriptor_handle: _Optional[str] = ..., operating_mode: _Optional[_Union[_types_pb2_1.OperatingMode, str]] = ...) -> None: ...

class SetComponentActivationAndSetOperatingModeRequest(_message.Message):
    __slots__ = ("component_metric_descriptor_handle", "component_activation", "operation_descriptor_handle", "operating_mode")
    COMPONENT_METRIC_DESCRIPTOR_HANDLE_FIELD_NUMBER: _ClassVar[int]
    COMPONENT_ACTIVATION_FIELD_NUMBER: _ClassVar[int]
    OPERATION_DESCRIPTOR_HANDLE_FIELD_NUMBER: _ClassVar[int]
    OPERATING_MODE_FIELD_NUMBER: _ClassVar[int]
    component_metric_descriptor_handle: str
    component_activation: _types_pb2_1_1.ComponentActivation
    operation_descriptor_handle: str
    operating_mode: _types_pb2_1.OperatingMode
    def __init__(self, component_metric_descriptor_handle: _Optional[str] = ..., component_activation: _Optional[_Union[_types_pb2_1_1.ComponentActivation, str]] = ..., operation_descriptor_handle: _Optional[str] = ..., operating_mode: _Optional[_Union[_types_pb2_1.OperatingMode, str]] = ...) -> None: ...

class SetAlertActivationAndSetOperatingModeRequest(_message.Message):
    __slots__ = ("alert_descriptor_handle", "alert_activation", "operation_descriptor_handle", "operating_mode")
    ALERT_DESCRIPTOR_HANDLE_FIELD_NUMBER: _ClassVar[int]
    ALERT_ACTIVATION_FIELD_NUMBER: _ClassVar[int]
    OPERATION_DESCRIPTOR_HANDLE_FIELD_NUMBER: _ClassVar[int]
    OPERATING_MODE_FIELD_NUMBER: _ClassVar[int]
    alert_descriptor_handle: str
    alert_activation: _types_pb2_1_1.AlertActivation
    operation_descriptor_handle: str
    operating_mode: _types_pb2_1.OperatingMode
    def __init__(self, alert_descriptor_handle: _Optional[str] = ..., alert_activation: _Optional[_Union[_types_pb2_1_1.AlertActivation, str]] = ..., operation_descriptor_handle: _Optional[str] = ..., operating_mode: _Optional[_Union[_types_pb2_1.OperatingMode, str]] = ...) -> None: ...

class SetModeOfOperationAndSetOperatingModeRequest(_message.Message):
    __slots__ = ("metric_descriptor_handle", "mode_of_operation", "operation_descriptor_handle", "operating_mode")
    METRIC_DESCRIPTOR_HANDLE_FIELD_NUMBER: _ClassVar[int]
    MODE_OF_OPERATION_FIELD_NUMBER: _ClassVar[int]
    OPERATION_DESCRIPTOR_HANDLE_FIELD_NUMBER: _ClassVar[int]
    OPERATING_MODE_FIELD_NUMBER: _ClassVar[int]
    metric_descriptor_handle: str
    mode_of_operation: _types_pb2_1_1_1.ModeOfOperation
    operation_descriptor_handle: str
    operating_mode: _types_pb2_1.OperatingMode
    def __init__(self, metric_descriptor_handle: _Optional[str] = ..., mode_of_operation: _Optional[_Union[_types_pb2_1_1_1.ModeOfOperation, str]] = ..., operation_descriptor_handle: _Optional[str] = ..., operating_mode: _Optional[_Union[_types_pb2_1.OperatingMode, str]] = ...) -> None: ...

class SetSystemContextActivationStateAndContextAssociationRequest(_message.Message):
    __slots__ = ("system_context_handle", "system_context_activation", "context_descriptor_handle", "context_association")
    SYSTEM_CONTEXT_HANDLE_FIELD_NUMBER: _ClassVar[int]
    SYSTEM_CONTEXT_ACTIVATION_FIELD_NUMBER: _ClassVar[int]
    CONTEXT_DESCRIPTOR_HANDLE_FIELD_NUMBER: _ClassVar[int]
    CONTEXT_ASSOCIATION_FIELD_NUMBER: _ClassVar[int]
    system_context_handle: str
    system_context_activation: _types_pb2_1_1.ComponentActivation
    context_descriptor_handle: str
    context_association: _types_pb2.ContextAssociation
    def __init__(self, system_context_handle: _Optional[str] = ..., system_context_activation: _Optional[_Union[_types_pb2_1_1.ComponentActivation, str]] = ..., context_descriptor_handle: _Optional[str] = ..., context_association: _Optional[_Union[_types_pb2.ContextAssociation, str]] = ...) -> None: ...
