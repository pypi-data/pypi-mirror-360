# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from enum import IntEnum
from ....protocol_enum_meta import ProtocolEnumMeta

class PartyReplyCode(IntEnum, metaclass=ProtocolEnumMeta):
    """
    Reply code sent with PARTY_REPLY packet.
    Indicates why an invite or join request failed.
    """
    AlreadyInAnotherParty = 0
    AlreadyInYourParty = 1
    PartyIsFull = 2
