# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from enum import IntEnum
from ....protocol_enum_meta import ProtocolEnumMeta

class GuildReply(IntEnum, metaclass=ProtocolEnumMeta):
    """
    Reply code sent with GUILD_REPLY packet
    """
    Busy = 1
    NotApproved = 2
    AlreadyMember = 3
    NoCandidates = 4
    Exists = 5
    CreateBegin = 6
    CreateAddConfirm = 7
    CreateAdd = 8
    RecruiterOffline = 9
    RecruiterNotHere = 10
    RecruiterWrongGuild = 11
    NotRecruiter = 12
    JoinRequest = 13
    NotPresent = 14
    AccountLow = 15
    Accepted = 16
    NotFound = 17
    Updated = 18
    RanksUpdated = 19
    RemoveLeader = 20
    RemoveNotMember = 21
    Removed = 22
    RankingLeader = 23
    RankingNotMember = 24
