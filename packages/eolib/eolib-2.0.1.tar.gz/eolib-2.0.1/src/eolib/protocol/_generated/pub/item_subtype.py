# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from enum import IntEnum
from ...protocol_enum_meta import ProtocolEnumMeta

class ItemSubtype(IntEnum, metaclass=ProtocolEnumMeta):
    None_ = 0
    Ranged = 1
    Arrows = 2
    Wings = 3
    Reserved4 = 4
