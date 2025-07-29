from t2iapi import response_types_pb2 as _response_types_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class BasicResponse(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: _response_types_pb2.Result
    def __init__(self, result: _Optional[_Union[_response_types_pb2.Result, str]] = ...) -> None: ...
