# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from enum import IntEnum
from ....protocol_enum_meta import ProtocolEnumMeta

class LoginReply(IntEnum, metaclass=ProtocolEnumMeta):
    """
    Reply code sent with LOGIN_REPLY packet.
    Indicates the result of a login attempt.
    """
    WrongUser = 1
    WrongUserPassword = 2
    Ok = 3
    Banned = 4
    """
    The official client won't display a message until the connection from the server is closed
    """
    LoggedIn = 5
    Busy = 6
    """
    The official client won't display a message until the connection from the server is closed
    """
