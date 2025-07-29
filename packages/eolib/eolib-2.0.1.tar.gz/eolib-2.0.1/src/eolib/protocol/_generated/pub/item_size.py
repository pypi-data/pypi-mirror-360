# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from enum import IntEnum
from ...protocol_enum_meta import ProtocolEnumMeta

class ItemSize(IntEnum, metaclass=ProtocolEnumMeta):
    """
    Size of an item in the inventory
    """
    Size1x1 = 0
    Size1x2 = 1
    Size1x3 = 2
    Size1x4 = 3
    Size2x1 = 4
    Size2x2 = 5
    Size2x3 = 6
    Size2x4 = 7
