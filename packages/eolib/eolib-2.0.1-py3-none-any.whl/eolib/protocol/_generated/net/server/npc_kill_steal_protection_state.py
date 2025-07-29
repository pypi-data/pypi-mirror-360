# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from enum import IntEnum
from ....protocol_enum_meta import ProtocolEnumMeta

class NpcKillStealProtectionState(IntEnum, metaclass=ProtocolEnumMeta):
    """
    Flag to indicate whether you are able to attack an NPC
    """
    Unprotected = 1
    Protected = 2
