# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from enum import IntEnum
from ...protocol_enum_meta import ProtocolEnumMeta

class ItemSpecial(IntEnum, metaclass=ProtocolEnumMeta):
    Normal = 0
    Rare = 1
    Legendary = 2
    Unique = 3
    Lore = 4
    Cursed = 5
