# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from enum import IntEnum
from ....protocol_enum_meta import ProtocolEnumMeta

class AdminMessageType(IntEnum, metaclass=ProtocolEnumMeta):
    """
    Type of message sent to admins via the Help menu
    """
    Message = 1
    Report = 2
