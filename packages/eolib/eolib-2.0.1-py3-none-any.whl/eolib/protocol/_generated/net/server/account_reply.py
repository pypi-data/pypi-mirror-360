# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from enum import IntEnum
from ....protocol_enum_meta import ProtocolEnumMeta

class AccountReply(IntEnum, metaclass=ProtocolEnumMeta):
    """
    Reply code sent with ACCOUNT_REPLY packet
    """
    Exists = 1
    NotApproved = 2
    Created = 3
    ChangeFailed = 5
    Changed = 6
    RequestDenied = 7
