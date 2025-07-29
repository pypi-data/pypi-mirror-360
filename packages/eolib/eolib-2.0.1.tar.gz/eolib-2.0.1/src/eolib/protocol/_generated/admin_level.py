# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from enum import IntEnum
from ..protocol_enum_meta import ProtocolEnumMeta

class AdminLevel(IntEnum, metaclass=ProtocolEnumMeta):
    """
    The admin level of a player
    """
    Player = 0
    Spy = 1
    LightGuide = 2
    Guardian = 3
    GameMaster = 4
    HighGameMaster = 5
