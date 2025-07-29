# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from enum import IntEnum
from ..protocol_enum_meta import ProtocolEnumMeta

class Direction(IntEnum, metaclass=ProtocolEnumMeta):
    """
    The direction a player or NPC is facing
    """
    Down = 0
    Left = 1
    Up = 2
    Right = 3
