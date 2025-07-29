# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from enum import IntEnum
from ..protocol_enum_meta import ProtocolEnumMeta

class Gender(IntEnum, metaclass=ProtocolEnumMeta):
    """
    The gender of a player
    """
    Female = 0
    Male = 1
