# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from enum import IntEnum
from ....protocol_enum_meta import ProtocolEnumMeta

class FileType(IntEnum, metaclass=ProtocolEnumMeta):
    """
    Data file type
    """
    Emf = 1
    Eif = 2
    Enf = 3
    Esf = 4
    Ecf = 5
