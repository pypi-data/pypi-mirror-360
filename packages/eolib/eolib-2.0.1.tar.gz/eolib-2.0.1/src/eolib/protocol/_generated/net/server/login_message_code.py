# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from enum import IntEnum
from ....protocol_enum_meta import ProtocolEnumMeta

class LoginMessageCode(IntEnum, metaclass=ProtocolEnumMeta):
    """
    Whether a warning message should be displayed upon entering the game
    """
    No = 0
    Yes = 2
