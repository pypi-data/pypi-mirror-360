# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from enum import IntEnum
from ...protocol_enum_meta import ProtocolEnumMeta

class SkillType(IntEnum, metaclass=ProtocolEnumMeta):
    Heal = 0
    Attack = 1
    Bard = 2
