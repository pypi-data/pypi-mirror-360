from t2iapi import basic_responses_pb2 as _basic_responses_pb2
from t2iapi import response_types_pb2 as _response_types_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CreateContextStateWithAssociationResponse(_message.Message):
    __slots__ = ("status", "context_state_handle")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    CONTEXT_STATE_HANDLE_FIELD_NUMBER: _ClassVar[int]
    status: _basic_responses_pb2.BasicResponse
    context_state_handle: str
    def __init__(self, status: _Optional[_Union[_basic_responses_pb2.BasicResponse, _Mapping]] = ..., context_state_handle: _Optional[str] = ...) -> None: ...

class EnsembleContextIndicateMembershipWithIdentificationResponse(_message.Message):
    __slots__ = ("status", "identification_list")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    IDENTIFICATION_LIST_FIELD_NUMBER: _ClassVar[int]
    status: _basic_responses_pb2.BasicResponse
    identification_list: _containers.RepeatedCompositeFieldContainer[_response_types_pb2.IdentificationList]
    def __init__(self, status: _Optional[_Union[_basic_responses_pb2.BasicResponse, _Mapping]] = ..., identification_list: _Optional[_Iterable[_Union[_response_types_pb2.IdentificationList, _Mapping]]] = ...) -> None: ...

class GetEnsembleIdsResponse(_message.Message):
    __slots__ = ("status", "ensemble_id")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    ENSEMBLE_ID_FIELD_NUMBER: _ClassVar[int]
    status: _basic_responses_pb2.BasicResponse
    ensemble_id: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, status: _Optional[_Union[_basic_responses_pb2.BasicResponse, _Mapping]] = ..., ensemble_id: _Optional[_Iterable[str]] = ...) -> None: ...

class IndicateMembershipInEnsembleByEnsembleIdResponse(_message.Message):
    __slots__ = ("status", "context_state_handle")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    CONTEXT_STATE_HANDLE_FIELD_NUMBER: _ClassVar[int]
    status: _basic_responses_pb2.BasicResponse
    context_state_handle: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, status: _Optional[_Union[_basic_responses_pb2.BasicResponse, _Mapping]] = ..., context_state_handle: _Optional[_Iterable[str]] = ...) -> None: ...
