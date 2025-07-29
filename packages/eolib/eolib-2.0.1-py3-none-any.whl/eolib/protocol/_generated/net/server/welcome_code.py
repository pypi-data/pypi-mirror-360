# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from enum import IntEnum
from ....protocol_enum_meta import ProtocolEnumMeta

class WelcomeCode(IntEnum, metaclass=ProtocolEnumMeta):
    """
    Reply code sent with WELCOME_REPLY packet
    """
    SelectCharacter = 1
    EnterGame = 2
    ServerBusy = 3
    LoggedIn = 4
