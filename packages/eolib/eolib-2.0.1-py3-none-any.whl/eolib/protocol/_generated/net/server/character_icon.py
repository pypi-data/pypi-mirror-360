# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from enum import IntEnum
from ....protocol_enum_meta import ProtocolEnumMeta

class CharacterIcon(IntEnum, metaclass=ProtocolEnumMeta):
    """
    Icon displayed in paperdolls, books, and the online list
    """
    Player = 1
    Gm = 4
    Hgm = 5
    Party = 6
    GmParty = 9
    HgmParty = 10
