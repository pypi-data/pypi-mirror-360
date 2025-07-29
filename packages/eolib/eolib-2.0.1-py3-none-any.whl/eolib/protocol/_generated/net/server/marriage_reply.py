# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from enum import IntEnum
from ....protocol_enum_meta import ProtocolEnumMeta

class MarriageReply(IntEnum, metaclass=ProtocolEnumMeta):
    """
    Reply code sent with MARRIAGE_REPLY packet
    """
    AlreadyMarried = 1
    NotMarried = 2
    Success = 3
    NotEnoughGold = 4
    WrongName = 5
    ServiceBusy = 6
    DivorceNotification = 7
