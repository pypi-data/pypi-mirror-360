# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from enum import IntEnum
from ....protocol_enum_meta import ProtocolEnumMeta

class InitBanType(IntEnum, metaclass=ProtocolEnumMeta):
    """
    Ban type sent with INIT_INIT packet.
    The official client treats a value &gt;= 2 as Permanent. Otherwise, it's Temporary.
    """
    Temporary = 1
    Permanent = 2
