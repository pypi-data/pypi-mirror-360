from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class LocalizedTextWidthMsg(_message.Message):
    __slots__ = ("enum_type",)
    class EnumType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        ENUM_TYPE_XS: _ClassVar[LocalizedTextWidthMsg.EnumType]
        ENUM_TYPE_S: _ClassVar[LocalizedTextWidthMsg.EnumType]
        ENUM_TYPE_M: _ClassVar[LocalizedTextWidthMsg.EnumType]
        ENUM_TYPE_L: _ClassVar[LocalizedTextWidthMsg.EnumType]
        ENUM_TYPE_XL: _ClassVar[LocalizedTextWidthMsg.EnumType]
        ENUM_TYPE_XXL: _ClassVar[LocalizedTextWidthMsg.EnumType]
    ENUM_TYPE_XS: LocalizedTextWidthMsg.EnumType
    ENUM_TYPE_S: LocalizedTextWidthMsg.EnumType
    ENUM_TYPE_M: LocalizedTextWidthMsg.EnumType
    ENUM_TYPE_L: LocalizedTextWidthMsg.EnumType
    ENUM_TYPE_XL: LocalizedTextWidthMsg.EnumType
    ENUM_TYPE_XXL: LocalizedTextWidthMsg.EnumType
    ENUM_TYPE_FIELD_NUMBER: _ClassVar[int]
    enum_type: LocalizedTextWidthMsg.EnumType
    def __init__(self, enum_type: _Optional[_Union[LocalizedTextWidthMsg.EnumType, str]] = ...) -> None: ...
