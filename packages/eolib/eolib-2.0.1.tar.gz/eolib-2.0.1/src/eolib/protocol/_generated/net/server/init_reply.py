# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from enum import IntEnum
from ....protocol_enum_meta import ProtocolEnumMeta

class InitReply(IntEnum, metaclass=ProtocolEnumMeta):
    """
    Reply code sent with INIT_INIT packet
    """
    OutOfDate = 1
    Ok = 2
    Banned = 3
    """
    The official client won't display a message until the connection from the server is closed
    """
    WarpMap = 4
    FileEmf = 5
    FileEif = 6
    FileEnf = 7
    FileEsf = 8
    PlayersList = 9
    MapMutation = 10
    PlayersListFriends = 11
    FileEcf = 12
