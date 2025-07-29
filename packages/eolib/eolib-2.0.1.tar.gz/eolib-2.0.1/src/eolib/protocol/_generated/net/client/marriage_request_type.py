# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from enum import IntEnum
from ....protocol_enum_meta import ProtocolEnumMeta

class MarriageRequestType(IntEnum, metaclass=ProtocolEnumMeta):
    """
    Request type sent with MARRIAGE_REQUEST packet
    """
    MarriageApproval = 1
    Divorce = 2
