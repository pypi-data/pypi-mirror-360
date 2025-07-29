# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from enum import IntEnum
from ....protocol_enum_meta import ProtocolEnumMeta

class TrainType(IntEnum, metaclass=ProtocolEnumMeta):
    """
    Whether the player is spending a stat point or a skill point
    """
    Stat = 1
    Skill = 2
