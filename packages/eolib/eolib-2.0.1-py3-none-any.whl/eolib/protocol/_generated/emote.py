# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from enum import IntEnum
from ..protocol_enum_meta import ProtocolEnumMeta

class Emote(IntEnum, metaclass=ProtocolEnumMeta):
    """
    Emote that can be played over a player's head
    """
    Happy = 1
    Depressed = 2
    Sad = 3
    Angry = 4
    Confused = 5
    Surprised = 6
    Hearts = 7
    Moon = 8
    Suicidal = 9
    Embarrassed = 10
    Drunk = 11
    Trade = 12
    LevelUp = 13
    Playful = 14
