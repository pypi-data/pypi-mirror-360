# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from enum import IntEnum
from ....protocol_enum_meta import ProtocolEnumMeta

class TalkReply(IntEnum, metaclass=ProtocolEnumMeta):
    """
    Reply code sent with TALK_REPLY packet
    """
    NotFound = 1
