from google.protobuf import wrappers_pb2 as _wrappers_pb2
from t2iapi.biceps import codedvalue_pb2 as _codedvalue_pb2
from t2iapi.biceps import localizedtext_pb2 as _localizedtext_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class InstanceIdentifierMsg(_message.Message):
    __slots__ = ("type", "identifier_name", "root_attr", "extension_attr")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    IDENTIFIER_NAME_FIELD_NUMBER: _ClassVar[int]
    ROOT_ATTR_FIELD_NUMBER: _ClassVar[int]
    EXTENSION_ATTR_FIELD_NUMBER: _ClassVar[int]
    type: _codedvalue_pb2.CodedValueMsg
    identifier_name: _containers.RepeatedCompositeFieldContainer[_localizedtext_pb2.LocalizedTextMsg]
    root_attr: _wrappers_pb2.StringValue
    extension_attr: _wrappers_pb2.StringValue
    def __init__(self, type: _Optional[_Union[_codedvalue_pb2.CodedValueMsg, _Mapping]] = ..., identifier_name: _Optional[_Iterable[_Union[_localizedtext_pb2.LocalizedTextMsg, _Mapping]]] = ..., root_attr: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., extension_attr: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ...) -> None: ...
