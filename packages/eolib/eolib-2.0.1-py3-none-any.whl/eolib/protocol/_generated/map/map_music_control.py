# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from enum import IntEnum
from ...protocol_enum_meta import ProtocolEnumMeta

class MapMusicControl(IntEnum, metaclass=ProtocolEnumMeta):
    """
    How background music should be played on a map
    """
    InterruptIfDifferentPlayOnce = 0
    InterruptPlayOnce = 1
    FinishPlayOnce = 2
    InterruptIfDifferentPlayRepeat = 3
    InterruptPlayRepeat = 4
    FinishPlayRepeat = 5
    InterruptPlayNothing = 6
