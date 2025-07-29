# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from enum import IntEnum
from ....protocol_enum_meta import ProtocolEnumMeta

class InnUnsubscribeReply(IntEnum, metaclass=ProtocolEnumMeta):
    """
    Reply code sent with CITIZEN_REMOVE packet.
    Indicates the result of trying to give up citizenship to a town.
    """
    NotCitizen = 0
    Unsubscribed = 1
