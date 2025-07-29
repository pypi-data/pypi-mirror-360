# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from enum import IntEnum
from ....protocol_enum_meta import ProtocolEnumMeta

class SkillMasterReply(IntEnum, metaclass=ProtocolEnumMeta):
    """
    Reply code sent with STATSKILL_REPLY packet.
    Indicates why an action was unsuccessful.
    """
    RemoveItems = 1
    WrongClass = 2
