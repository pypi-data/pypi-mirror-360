from t2iapi.biceps import localizedtext_pb2 as _localizedtext_pb2
from t2iapi.biceps import instanceidentifier_pb2 as _instanceidentifier_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class MetaDataMsg(_message.Message):
    __slots__ = ("udi", "lot_number", "manufacturer", "manufacture_date", "expiration_date", "model_name", "model_number", "serial_number")
    class UdiMsg(_message.Message):
        __slots__ = ("device_identifier", "human_readable_form", "issuer", "jurisdiction")
        DEVICE_IDENTIFIER_FIELD_NUMBER: _ClassVar[int]
        HUMAN_READABLE_FORM_FIELD_NUMBER: _ClassVar[int]
        ISSUER_FIELD_NUMBER: _ClassVar[int]
        JURISDICTION_FIELD_NUMBER: _ClassVar[int]
        device_identifier: str
        human_readable_form: str
        issuer: _instanceidentifier_pb2.InstanceIdentifierMsg
        jurisdiction: _instanceidentifier_pb2.InstanceIdentifierMsg
        def __init__(self, device_identifier: _Optional[str] = ..., human_readable_form: _Optional[str] = ..., issuer: _Optional[_Union[_instanceidentifier_pb2.InstanceIdentifierMsg, _Mapping]] = ..., jurisdiction: _Optional[_Union[_instanceidentifier_pb2.InstanceIdentifierMsg, _Mapping]] = ...) -> None: ...
    UDI_FIELD_NUMBER: _ClassVar[int]
    LOT_NUMBER_FIELD_NUMBER: _ClassVar[int]
    MANUFACTURER_FIELD_NUMBER: _ClassVar[int]
    MANUFACTURE_DATE_FIELD_NUMBER: _ClassVar[int]
    EXPIRATION_DATE_FIELD_NUMBER: _ClassVar[int]
    MODEL_NAME_FIELD_NUMBER: _ClassVar[int]
    MODEL_NUMBER_FIELD_NUMBER: _ClassVar[int]
    SERIAL_NUMBER_FIELD_NUMBER: _ClassVar[int]
    udi: _containers.RepeatedCompositeFieldContainer[MetaDataMsg.UdiMsg]
    lot_number: _wrappers_pb2.StringValue
    manufacturer: _containers.RepeatedCompositeFieldContainer[_localizedtext_pb2.LocalizedTextMsg]
    manufacture_date: _wrappers_pb2.StringValue
    expiration_date: _wrappers_pb2.StringValue
    model_name: _containers.RepeatedCompositeFieldContainer[_localizedtext_pb2.LocalizedTextMsg]
    model_number: _wrappers_pb2.StringValue
    serial_number: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, udi: _Optional[_Iterable[_Union[MetaDataMsg.UdiMsg, _Mapping]]] = ..., lot_number: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., manufacturer: _Optional[_Iterable[_Union[_localizedtext_pb2.LocalizedTextMsg, _Mapping]]] = ..., manufacture_date: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., expiration_date: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., model_name: _Optional[_Iterable[_Union[_localizedtext_pb2.LocalizedTextMsg, _Mapping]]] = ..., model_number: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., serial_number: _Optional[_Iterable[str]] = ...) -> None: ...
