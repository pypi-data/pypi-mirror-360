# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from enum import IntEnum
from ....protocol_enum_meta import ProtocolEnumMeta

class AvatarChangeType(IntEnum, metaclass=ProtocolEnumMeta):
    """
    How a player's appearance is changing
    """
    Equipment = 1
    Hair = 2
    HairColor = 3
