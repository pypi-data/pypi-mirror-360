# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from enum import IntEnum
from ....protocol_enum_meta import ProtocolEnumMeta

class MapDamageType(IntEnum, metaclass=ProtocolEnumMeta):
    """
    Type of damage being caused by the environment
    """
    TpDrain = 1
    Spikes = 2
