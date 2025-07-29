# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from enum import IntEnum
from ....protocol_enum_meta import ProtocolEnumMeta

class PlayerKilledState(IntEnum, metaclass=ProtocolEnumMeta):
    """
    Flag to indicate that a player has been killed
    """
    Alive = 1
    Killed = 2
