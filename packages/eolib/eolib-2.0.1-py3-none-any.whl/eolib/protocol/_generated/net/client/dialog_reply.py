# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from enum import IntEnum
from ....protocol_enum_meta import ProtocolEnumMeta

class DialogReply(IntEnum, metaclass=ProtocolEnumMeta):
    """
    Whether the player has clicked the OK button or a link in a quest dialog
    """
    Ok = 1
    Link = 2
