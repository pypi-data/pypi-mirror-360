# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from enum import IntEnum
from ....protocol_enum_meta import ProtocolEnumMeta

class GuildInfoType(IntEnum, metaclass=ProtocolEnumMeta):
    """
    The type of guild info being interacted with
    """
    Description = 1
    Ranks = 2
    Bank = 3
