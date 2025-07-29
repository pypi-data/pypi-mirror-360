# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from enum import IntEnum
from ...protocol_enum_meta import ProtocolEnumMeta

class Element(IntEnum, metaclass=ProtocolEnumMeta):
    None_ = 0
    Light = 1
    Dark = 2
    Earth = 3
    Wind = 4
    Water = 5
    Fire = 6
