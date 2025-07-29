# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from enum import IntEnum
from ....protocol_enum_meta import ProtocolEnumMeta

class StatId(IntEnum, metaclass=ProtocolEnumMeta):
    """
    Base character stat
    """
    Str = 1
    Int = 2
    Wis = 3
    Agi = 4
    Con = 5
    Cha = 6
