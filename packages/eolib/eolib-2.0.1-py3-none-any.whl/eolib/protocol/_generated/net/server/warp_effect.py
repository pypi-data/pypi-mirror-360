# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from enum import IntEnum
from ....protocol_enum_meta import ProtocolEnumMeta

class WarpEffect(IntEnum, metaclass=ProtocolEnumMeta):
    """
    An effect that accompanies a player warp
    """
    None_ = 0
    """
    Does nothing
    """
    Scroll = 1
    """
    Plays the scroll sound effect
    """
    Admin = 2
    """
    Plays the admin warp sound effect and animation
    """
