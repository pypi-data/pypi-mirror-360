# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from enum import IntEnum
from ....protocol_enum_meta import ProtocolEnumMeta

class SitState(IntEnum, metaclass=ProtocolEnumMeta):
    """
    Indicates how a player is sitting (or not sitting)
    """
    Stand = 0
    Chair = 1
    Floor = 2
