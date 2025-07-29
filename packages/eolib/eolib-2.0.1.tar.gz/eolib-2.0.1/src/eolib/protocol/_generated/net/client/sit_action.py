# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from enum import IntEnum
from ....protocol_enum_meta import ProtocolEnumMeta

class SitAction(IntEnum, metaclass=ProtocolEnumMeta):
    """
    Whether the player wants to sit or stand
    """
    Sit = 1
    Stand = 2
