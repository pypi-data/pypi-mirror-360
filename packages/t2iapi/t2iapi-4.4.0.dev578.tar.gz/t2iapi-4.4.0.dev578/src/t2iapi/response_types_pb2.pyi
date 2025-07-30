from google.protobuf import wrappers_pb2 as _wrappers_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Result(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    RESULT_FAIL: _ClassVar[Result]
    RESULT_SUCCESS: _ClassVar[Result]
    RESULT_NOT_SUPPORTED: _ClassVar[Result]
    RESULT_NOT_IMPLEMENTED: _ClassVar[Result]
RESULT_FAIL: Result
RESULT_SUCCESS: Result
RESULT_NOT_SUPPORTED: Result
RESULT_NOT_IMPLEMENTED: Result

class IdentificationList(_message.Message):
    __slots__ = ("identification",)
    IDENTIFICATION_FIELD_NUMBER: _ClassVar[int]
    identification: _containers.RepeatedCompositeFieldContainer[PartialInstanceIdentifier]
    def __init__(self, identification: _Optional[_Iterable[_Union[PartialInstanceIdentifier, _Mapping]]] = ...) -> None: ...

class PartialInstanceIdentifier(_message.Message):
    __slots__ = ("root", "extension", "identification_type")
    ROOT_FIELD_NUMBER: _ClassVar[int]
    EXTENSION_FIELD_NUMBER: _ClassVar[int]
    IDENTIFICATION_TYPE_FIELD_NUMBER: _ClassVar[int]
    root: _wrappers_pb2.StringValue
    extension: _wrappers_pb2.StringValue
    identification_type: PartialCodedValue
    def __init__(self, root: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., extension: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., identification_type: _Optional[_Union[PartialCodedValue, _Mapping]] = ...) -> None: ...

class PartialCodedValue(_message.Message):
    __slots__ = ("translations",)
    TRANSLATIONS_FIELD_NUMBER: _ClassVar[int]
    translations: _containers.RepeatedCompositeFieldContainer[Translation]
    def __init__(self, translations: _Optional[_Iterable[_Union[Translation, _Mapping]]] = ...) -> None: ...

class Translation(_message.Message):
    __slots__ = ("translation_code", "coding_system", "coding_system_version")
    TRANSLATION_CODE_FIELD_NUMBER: _ClassVar[int]
    CODING_SYSTEM_FIELD_NUMBER: _ClassVar[int]
    CODING_SYSTEM_VERSION_FIELD_NUMBER: _ClassVar[int]
    translation_code: str
    coding_system: str
    coding_system_version: _wrappers_pb2.StringValue
    def __init__(self, translation_code: _Optional[str] = ..., coding_system: _Optional[str] = ..., coding_system_version: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ...) -> None: ...
