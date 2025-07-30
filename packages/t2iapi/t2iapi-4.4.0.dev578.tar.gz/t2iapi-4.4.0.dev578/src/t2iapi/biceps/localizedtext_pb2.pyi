from google.protobuf import wrappers_pb2 as _wrappers_pb2
from t2iapi.biceps import localizedtextwidth_pb2 as _localizedtextwidth_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class LocalizedTextMsg(_message.Message):
    __slots__ = ("localized_text_content", "ref_attr", "lang_attr", "version_attr", "text_width_attr")
    LOCALIZED_TEXT_CONTENT_FIELD_NUMBER: _ClassVar[int]
    REF_ATTR_FIELD_NUMBER: _ClassVar[int]
    LANG_ATTR_FIELD_NUMBER: _ClassVar[int]
    VERSION_ATTR_FIELD_NUMBER: _ClassVar[int]
    TEXT_WIDTH_ATTR_FIELD_NUMBER: _ClassVar[int]
    localized_text_content: _wrappers_pb2.StringValue
    ref_attr: _wrappers_pb2.StringValue
    lang_attr: _wrappers_pb2.StringValue
    version_attr: _wrappers_pb2.UInt64Value
    text_width_attr: _localizedtextwidth_pb2.LocalizedTextWidthMsg
    def __init__(self, localized_text_content: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., ref_attr: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., lang_attr: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., version_attr: _Optional[_Union[_wrappers_pb2.UInt64Value, _Mapping]] = ..., text_width_attr: _Optional[_Union[_localizedtextwidth_pb2.LocalizedTextWidthMsg, _Mapping]] = ...) -> None: ...
