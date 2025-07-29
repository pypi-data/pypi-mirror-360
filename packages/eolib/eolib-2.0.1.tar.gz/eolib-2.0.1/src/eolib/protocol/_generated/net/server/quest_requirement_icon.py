# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from enum import IntEnum
from ....protocol_enum_meta import ProtocolEnumMeta

class QuestRequirementIcon(IntEnum, metaclass=ProtocolEnumMeta):
    """
    Icon displayed for each quest in the Quest Progress window
    """
    Item = 3
    Talk = 5
    Kill = 8
    Step = 10
