from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from typing import ClassVar as _ClassVar

DESCRIPTOR: _descriptor.FileDescriptor

class ComponentActivation(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    COMPONENT_ACTIVATION_ON: _ClassVar[ComponentActivation]
    COMPONENT_ACTIVATION_NOT_READY: _ClassVar[ComponentActivation]
    COMPONENT_ACTIVATION_STANDBY: _ClassVar[ComponentActivation]
    COMPONENT_ACTIVATION_OFF: _ClassVar[ComponentActivation]
    COMPONENT_ACTIVATION_SHUTDOWN: _ClassVar[ComponentActivation]
    COMPONENT_ACTIVATION_FAILURE: _ClassVar[ComponentActivation]

class AlertActivation(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ALERT_ACTIVATION_ON: _ClassVar[AlertActivation]
    ALERT_ACTIVATION_OFF: _ClassVar[AlertActivation]
    ALERT_ACTIVATION_PSD: _ClassVar[AlertActivation]

class AlertSignalManifestation(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ALERT_SIGNAL_MANIFESTATION_AUD: _ClassVar[AlertSignalManifestation]
    ALERT_SIGNAL_MANIFESTATION_VIS: _ClassVar[AlertSignalManifestation]
    ALERT_SIGNAL_MANIFESTATION_TAN: _ClassVar[AlertSignalManifestation]
    ALERT_SIGNAL_MANIFESTATION_OTH: _ClassVar[AlertSignalManifestation]
COMPONENT_ACTIVATION_ON: ComponentActivation
COMPONENT_ACTIVATION_NOT_READY: ComponentActivation
COMPONENT_ACTIVATION_STANDBY: ComponentActivation
COMPONENT_ACTIVATION_OFF: ComponentActivation
COMPONENT_ACTIVATION_SHUTDOWN: ComponentActivation
COMPONENT_ACTIVATION_FAILURE: ComponentActivation
ALERT_ACTIVATION_ON: AlertActivation
ALERT_ACTIVATION_OFF: AlertActivation
ALERT_ACTIVATION_PSD: AlertActivation
ALERT_SIGNAL_MANIFESTATION_AUD: AlertSignalManifestation
ALERT_SIGNAL_MANIFESTATION_VIS: AlertSignalManifestation
ALERT_SIGNAL_MANIFESTATION_TAN: AlertSignalManifestation
ALERT_SIGNAL_MANIFESTATION_OTH: AlertSignalManifestation
