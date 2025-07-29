# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from enum import IntEnum
from ....protocol_enum_meta import ProtocolEnumMeta

class DialogEntryType(IntEnum, metaclass=ProtocolEnumMeta):
    """
    The type of an entry in a quest dialog
    """
    Text = 1
    Link = 2
