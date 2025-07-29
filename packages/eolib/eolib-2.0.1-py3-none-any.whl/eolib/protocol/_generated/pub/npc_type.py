# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from enum import IntEnum
from ...protocol_enum_meta import ProtocolEnumMeta

class NpcType(IntEnum, metaclass=ProtocolEnumMeta):
    Friendly = 0
    Passive = 1
    Aggressive = 2
    Reserved3 = 3
    Reserved4 = 4
    Reserved5 = 5
    Shop = 6
    Inn = 7
    Reserved8 = 8
    Bank = 9
    Barber = 10
    Guild = 11
    Priest = 12
    Lawyer = 13
    Trainer = 14
    Quest = 15
