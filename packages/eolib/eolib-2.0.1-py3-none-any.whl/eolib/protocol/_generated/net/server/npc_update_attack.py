# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from .player_killed_state import PlayerKilledState
from ...direction import Direction
from ....serialization_error import SerializationError
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class NpcUpdateAttack:
    """
    An NPC attacking
    """
    _byte_size: int = 0
    _npc_index: int
    _killed: PlayerKilledState
    _direction: Direction
    _player_id: int
    _damage: int
    _hp_percentage: int

    def __init__(self, *, npc_index: int, killed: PlayerKilledState, direction: Direction, player_id: int, damage: int, hp_percentage: int):
        """
        Create a new instance of NpcUpdateAttack.

        Args:
            npc_index (int): (Value range is 0-252.)
            killed (PlayerKilledState): 
            direction (Direction): 
            player_id (int): (Value range is 0-64008.)
            damage (int): (Value range is 0-16194276.)
            hp_percentage (int): (Value range is 0-252.)
        """
        self._npc_index = npc_index
        self._killed = killed
        self._direction = direction
        self._player_id = player_id
        self._damage = damage
        self._hp_percentage = hp_percentage

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def npc_index(self) -> int:
        return self._npc_index

    @property
    def killed(self) -> PlayerKilledState:
        return self._killed

    @property
    def direction(self) -> Direction:
        return self._direction

    @property
    def player_id(self) -> int:
        return self._player_id

    @property
    def damage(self) -> int:
        return self._damage

    @property
    def hp_percentage(self) -> int:
        return self._hp_percentage

    @staticmethod
    def serialize(writer: EoWriter, data: "NpcUpdateAttack") -> None:
        """
        Serializes an instance of `NpcUpdateAttack` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (NpcUpdateAttack): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._npc_index is None:
                raise SerializationError("npc_index must be provided.")
            writer.add_char(data._npc_index)
            if data._killed is None:
                raise SerializationError("killed must be provided.")
            writer.add_char(int(data._killed))
            if data._direction is None:
                raise SerializationError("direction must be provided.")
            writer.add_char(int(data._direction))
            if data._player_id is None:
                raise SerializationError("player_id must be provided.")
            writer.add_short(data._player_id)
            if data._damage is None:
                raise SerializationError("damage must be provided.")
            writer.add_three(data._damage)
            if data._hp_percentage is None:
                raise SerializationError("hp_percentage must be provided.")
            writer.add_char(data._hp_percentage)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "NpcUpdateAttack":
        """
        Deserializes an instance of `NpcUpdateAttack` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            NpcUpdateAttack: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            npc_index = reader.get_char()
            killed = PlayerKilledState(reader.get_char())
            direction = Direction(reader.get_char())
            player_id = reader.get_short()
            damage = reader.get_three()
            hp_percentage = reader.get_char()
            result = NpcUpdateAttack(npc_index=npc_index, killed=killed, direction=direction, player_id=player_id, damage=damage, hp_percentage=hp_percentage)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"NpcUpdateAttack(byte_size={repr(self._byte_size)}, npc_index={repr(self._npc_index)}, killed={repr(self._killed)}, direction={repr(self._direction)}, player_id={repr(self._player_id)}, damage={repr(self._damage)}, hp_percentage={repr(self._hp_percentage)})"
