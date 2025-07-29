# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from enum import IntEnum
from ...protocol_enum_meta import ProtocolEnumMeta

class SkillTargetType(IntEnum, metaclass=ProtocolEnumMeta):
    Normal = 0
    Self = 1
    Reserved2 = 2
    Group = 3
