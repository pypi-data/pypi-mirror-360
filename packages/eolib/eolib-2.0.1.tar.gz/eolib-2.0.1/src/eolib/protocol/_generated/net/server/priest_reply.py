# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from enum import IntEnum
from ....protocol_enum_meta import ProtocolEnumMeta

class PriestReply(IntEnum, metaclass=ProtocolEnumMeta):
    """
    Reply code sent with PRIEST_REPLY packet
    """
    NotDressed = 1
    LowLevel = 2
    PartnerNotPresent = 3
    PartnerNotDressed = 4
    Busy = 5
    DoYou = 6
    PartnerAlreadyMarried = 7
    NoPermission = 8
