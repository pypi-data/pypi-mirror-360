from t2iapi.biceps import localizedtext_pb2 as _localizedtext_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CodedValueMsg(_message.Message):
    __slots__ = ("coding_system_name", "concept_description", "translation", "code_attr", "coding_system_attr", "coding_system_version_attr", "symbolic_code_name_attr")
    class TranslationMsg(_message.Message):
        __slots__ = ("code_attr", "coding_system_attr", "coding_system_version_attr")
        CODE_ATTR_FIELD_NUMBER: _ClassVar[int]
        CODING_SYSTEM_ATTR_FIELD_NUMBER: _ClassVar[int]
        CODING_SYSTEM_VERSION_ATTR_FIELD_NUMBER: _ClassVar[int]
        code_attr: str
        coding_system_attr: _wrappers_pb2.StringValue
        coding_system_version_attr: _wrappers_pb2.StringValue
        def __init__(self, code_attr: _Optional[str] = ..., coding_system_attr: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., coding_system_version_attr: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ...) -> None: ...
    CODING_SYSTEM_NAME_FIELD_NUMBER: _ClassVar[int]
    CONCEPT_DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    TRANSLATION_FIELD_NUMBER: _ClassVar[int]
    CODE_ATTR_FIELD_NUMBER: _ClassVar[int]
    CODING_SYSTEM_ATTR_FIELD_NUMBER: _ClassVar[int]
    CODING_SYSTEM_VERSION_ATTR_FIELD_NUMBER: _ClassVar[int]
    SYMBOLIC_CODE_NAME_ATTR_FIELD_NUMBER: _ClassVar[int]
    coding_system_name: _containers.RepeatedCompositeFieldContainer[_localizedtext_pb2.LocalizedTextMsg]
    concept_description: _containers.RepeatedCompositeFieldContainer[_localizedtext_pb2.LocalizedTextMsg]
    translation: _containers.RepeatedCompositeFieldContainer[CodedValueMsg.TranslationMsg]
    code_attr: str
    coding_system_attr: _wrappers_pb2.StringValue
    coding_system_version_attr: _wrappers_pb2.StringValue
    symbolic_code_name_attr: _wrappers_pb2.StringValue
    def __init__(self, coding_system_name: _Optional[_Iterable[_Union[_localizedtext_pb2.LocalizedTextMsg, _Mapping]]] = ..., concept_description: _Optional[_Iterable[_Union[_localizedtext_pb2.LocalizedTextMsg, _Mapping]]] = ..., translation: _Optional[_Iterable[_Union[CodedValueMsg.TranslationMsg, _Mapping]]] = ..., code_attr: _Optional[str] = ..., coding_system_attr: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., coding_system_version_attr: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., symbolic_code_name_attr: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ...) -> None: ...
