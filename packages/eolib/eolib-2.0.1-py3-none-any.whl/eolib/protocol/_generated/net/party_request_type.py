# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from enum import IntEnum
from ...protocol_enum_meta import ProtocolEnumMeta

class PartyRequestType(IntEnum, metaclass=ProtocolEnumMeta):
    """
    Whether a player is requesting to join a party, or inviting someone to join theirs
    """
    Join = 0
    Invite = 1
