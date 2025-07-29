# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from enum import IntEnum
from ...protocol_enum_meta import ProtocolEnumMeta

class PacketAction(IntEnum, metaclass=ProtocolEnumMeta):
    """
    The specific action that a packet performs.
    Part of the unique packet ID.
    """
    Request = 1
    Accept = 2
    Reply = 3
    Remove = 4
    Agree = 5
    Create = 6
    Add = 7
    Player = 8
    Take = 9
    Use = 10
    Buy = 11
    Sell = 12
    Open = 13
    Close = 14
    Msg = 15
    Spec = 16
    Admin = 17
    List = 18
    Tell = 20
    Report = 21
    Announce = 22
    Server = 23
    Drop = 24
    Junk = 25
    Obtain = 26
    Get = 27
    Kick = 28
    Rank = 29
    TargetSelf = 30
    TargetOther = 31
    TargetGroup = 33
    Dialog = 34
    Ping = 240
    Pong = 241
    Net242 = 242
    Net243 = 243
    Net244 = 244
    Error = 250
    Init = 255
