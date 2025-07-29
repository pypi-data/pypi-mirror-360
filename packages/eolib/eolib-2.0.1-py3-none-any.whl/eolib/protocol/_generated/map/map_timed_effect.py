# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from enum import IntEnum
from ...protocol_enum_meta import ProtocolEnumMeta

class MapTimedEffect(IntEnum, metaclass=ProtocolEnumMeta):
    """
    A timed effect that can occur on a map
    """
    None_ = 0
    HpDrain = 1
    TpDrain = 2
    Quake1 = 3
    Quake2 = 4
    Quake3 = 5
    Quake4 = 6
