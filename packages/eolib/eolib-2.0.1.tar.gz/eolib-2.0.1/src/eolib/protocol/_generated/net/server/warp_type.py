# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from enum import IntEnum
from ....protocol_enum_meta import ProtocolEnumMeta

class WarpType(IntEnum, metaclass=ProtocolEnumMeta):
    """
    Indicates whether a warp is within the current map, or switching to another map
    """
    Local = 1
    MapSwitch = 2
