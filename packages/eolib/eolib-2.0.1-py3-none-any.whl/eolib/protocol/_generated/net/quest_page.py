# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from enum import IntEnum
from ...protocol_enum_meta import ProtocolEnumMeta

class QuestPage(IntEnum, metaclass=ProtocolEnumMeta):
    """
    A page in the Quest menu
    """
    Progress = 1
    History = 2
