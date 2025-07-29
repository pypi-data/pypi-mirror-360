# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from enum import IntEnum
from ...protocol_enum_meta import ProtocolEnumMeta

class MapTileSpec(IntEnum, metaclass=ProtocolEnumMeta):
    """
    The type of a tile on a map
    """
    Wall = 0
    ChairDown = 1
    ChairLeft = 2
    ChairRight = 3
    ChairUp = 4
    ChairDownRight = 5
    ChairUpLeft = 6
    ChairAll = 7
    Reserved8 = 8
    Chest = 9
    Reserved10 = 10
    Reserved11 = 11
    Reserved12 = 12
    Reserved13 = 13
    Reserved14 = 14
    Reserved15 = 15
    BankVault = 16
    NpcBoundary = 17
    Edge = 18
    FakeWall = 19
    Board1 = 20
    Board2 = 21
    Board3 = 22
    Board4 = 23
    Board5 = 24
    Board6 = 25
    Board7 = 26
    Board8 = 27
    Jukebox = 28
    Jump = 29
    Water = 30
    Reserved31 = 31
    Arena = 32
    AmbientSource = 33
    TimedSpikes = 34
    Spikes = 35
    HiddenSpikes = 36
