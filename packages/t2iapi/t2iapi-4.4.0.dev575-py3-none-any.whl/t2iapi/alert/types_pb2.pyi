from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from typing import ClassVar as _ClassVar

DESCRIPTOR: _descriptor.FileDescriptor

class AlertSignalPresence(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ALERT_SIGNAL_PRESENCE_ON: _ClassVar[AlertSignalPresence]
    ALERT_SIGNAL_PRESENCE_OFF: _ClassVar[AlertSignalPresence]
    ALERT_SIGNAL_PRESENCE_LATCH: _ClassVar[AlertSignalPresence]
    ALERT_SIGNAL_PRESENCE_ACK: _ClassVar[AlertSignalPresence]
ALERT_SIGNAL_PRESENCE_ON: AlertSignalPresence
ALERT_SIGNAL_PRESENCE_OFF: AlertSignalPresence
ALERT_SIGNAL_PRESENCE_LATCH: AlertSignalPresence
ALERT_SIGNAL_PRESENCE_ACK: AlertSignalPresence
