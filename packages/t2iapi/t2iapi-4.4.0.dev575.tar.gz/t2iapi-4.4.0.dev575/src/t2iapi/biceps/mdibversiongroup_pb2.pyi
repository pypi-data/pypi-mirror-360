from google.protobuf import wrappers_pb2 as _wrappers_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class MdibVersionGroup(_message.Message):
    __slots__ = ("mdib_version", "sequence_id", "instance_id")
    MDIB_VERSION_FIELD_NUMBER: _ClassVar[int]
    SEQUENCE_ID_FIELD_NUMBER: _ClassVar[int]
    INSTANCE_ID_FIELD_NUMBER: _ClassVar[int]
    mdib_version: _wrappers_pb2.UInt64Value
    sequence_id: str
    instance_id: _wrappers_pb2.UInt64Value
    def __init__(self, mdib_version: _Optional[_Union[_wrappers_pb2.UInt64Value, _Mapping]] = ..., sequence_id: _Optional[str] = ..., instance_id: _Optional[_Union[_wrappers_pb2.UInt64Value, _Mapping]] = ...) -> None: ...
