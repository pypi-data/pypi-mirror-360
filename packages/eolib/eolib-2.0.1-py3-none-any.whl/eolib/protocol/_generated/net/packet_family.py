# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from enum import IntEnum
from ...protocol_enum_meta import ProtocolEnumMeta

class PacketFamily(IntEnum, metaclass=ProtocolEnumMeta):
    """
    The type of operation that a packet performs.
    Part of the unique packet ID.
    """
    Connection = 1
    Account = 2
    Character = 3
    Login = 4
    Welcome = 5
    Walk = 6
    Face = 7
    Chair = 8
    Emote = 9
    Attack = 11
    Spell = 12
    Shop = 13
    Item = 14
    StatSkill = 16
    Global = 17
    Talk = 18
    Warp = 19
    Jukebox = 21
    Players = 22
    Avatar = 23
    Party = 24
    Refresh = 25
    Npc = 26
    PlayerRange = 27
    NpcRange = 28
    Range = 29
    Paperdoll = 30
    Effect = 31
    Trade = 32
    Chest = 33
    Door = 34
    Message = 35
    Bank = 36
    Locker = 37
    Barber = 38
    Guild = 39
    Music = 40
    Sit = 41
    Recover = 42
    Board = 43
    Cast = 44
    Arena = 45
    Priest = 46
    Marriage = 47
    AdminInteract = 48
    Citizen = 49
    Quest = 50
    Book = 51
    Error = 250
    Init = 255
