# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from enum import IntEnum
from ...protocol_enum_meta import ProtocolEnumMeta

class SkillTargetRestrict(IntEnum, metaclass=ProtocolEnumMeta):
    Npc = 0
    Friendly = 1
    Opponent = 2
