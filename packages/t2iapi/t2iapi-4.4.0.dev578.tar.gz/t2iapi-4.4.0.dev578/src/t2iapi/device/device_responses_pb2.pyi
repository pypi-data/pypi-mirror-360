from t2iapi import basic_responses_pb2 as _basic_responses_pb2
from t2iapi.biceps import metadata_pb2 as _metadata_pb2
from t2iapi.biceps import mdibversiongroup_pb2 as _mdibversiongroup_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetMdsUiSupportedLanguagesResponse(_message.Message):
    __slots__ = ("status", "languages")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    LANGUAGES_FIELD_NUMBER: _ClassVar[int]
    status: _basic_responses_pb2.BasicResponse
    languages: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, status: _Optional[_Union[_basic_responses_pb2.BasicResponse, _Mapping]] = ..., languages: _Optional[_Iterable[str]] = ...) -> None: ...

class GetRemovableDescriptorsResponse(_message.Message):
    __slots__ = ("status", "handle")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    HANDLE_FIELD_NUMBER: _ClassVar[int]
    status: _basic_responses_pb2.BasicResponse
    handle: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, status: _Optional[_Union[_basic_responses_pb2.BasicResponse, _Mapping]] = ..., handle: _Optional[_Iterable[str]] = ...) -> None: ...

class AvailableDeviceMetaDataResponse(_message.Message):
    __slots__ = ("status", "meta_data")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    META_DATA_FIELD_NUMBER: _ClassVar[int]
    status: _basic_responses_pb2.BasicResponse
    meta_data: _metadata_pb2.MetaDataMsg
    def __init__(self, status: _Optional[_Union[_basic_responses_pb2.BasicResponse, _Mapping]] = ..., meta_data: _Optional[_Union[_metadata_pb2.MetaDataMsg, _Mapping]] = ...) -> None: ...

class GetComponentSwVersionResponse(_message.Message):
    __slots__ = ("status", "software_version")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    SOFTWARE_VERSION_FIELD_NUMBER: _ClassVar[int]
    status: _basic_responses_pb2.BasicResponse
    software_version: str
    def __init__(self, status: _Optional[_Union[_basic_responses_pb2.BasicResponse, _Mapping]] = ..., software_version: _Optional[str] = ...) -> None: ...

class GetComponentHwVersionResponse(_message.Message):
    __slots__ = ("status", "hardware_version")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    HARDWARE_VERSION_FIELD_NUMBER: _ClassVar[int]
    status: _basic_responses_pb2.BasicResponse
    hardware_version: str
    def __init__(self, status: _Optional[_Union[_basic_responses_pb2.BasicResponse, _Mapping]] = ..., hardware_version: _Optional[str] = ...) -> None: ...

class InsertContainmentTreeEntryForSequenceIdResponse(_message.Message):
    __slots__ = ("status", "handle")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    HANDLE_FIELD_NUMBER: _ClassVar[int]
    status: _basic_responses_pb2.BasicResponse
    handle: str
    def __init__(self, status: _Optional[_Union[_basic_responses_pb2.BasicResponse, _Mapping]] = ..., handle: _Optional[str] = ...) -> None: ...

class IndicateTimeOfNextCalibrationToUserResponse(_message.Message):
    __slots__ = ("status", "mdib_version_group")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    MDIB_VERSION_GROUP_FIELD_NUMBER: _ClassVar[int]
    status: _basic_responses_pb2.BasicResponse
    mdib_version_group: _mdibversiongroup_pb2.MdibVersionGroup
    def __init__(self, status: _Optional[_Union[_basic_responses_pb2.BasicResponse, _Mapping]] = ..., mdib_version_group: _Optional[_Union[_mdibversiongroup_pb2.MdibVersionGroup, _Mapping]] = ...) -> None: ...

class ProductionSpecificationElementResponse(_message.Message):
    __slots__ = ("status", "handle")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    HANDLE_FIELD_NUMBER: _ClassVar[int]
    status: _basic_responses_pb2.BasicResponse
    handle: str
    def __init__(self, status: _Optional[_Union[_basic_responses_pb2.BasicResponse, _Mapping]] = ..., handle: _Optional[str] = ...) -> None: ...
