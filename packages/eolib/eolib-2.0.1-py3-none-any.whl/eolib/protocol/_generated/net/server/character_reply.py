# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from enum import IntEnum
from ....protocol_enum_meta import ProtocolEnumMeta

class CharacterReply(IntEnum, metaclass=ProtocolEnumMeta):
    """
    Reply code sent with CHARACTER_REPLY packet
    """
    Exists = 1
    Full = 2
    """
    Only sent in reply to Character_Create packets.
    Displays the same message as CharacterReply.Full3 in the official client.
    """
    Full3 = 3
    """
    Only sent in reply to Character_Request packets.
    Displays the same message as CharacterReply.Full in the official client.
    """
    NotApproved = 4
    Ok = 5
    Deleted = 6
