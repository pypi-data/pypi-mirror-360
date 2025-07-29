# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from ....serialization_error import SerializationError
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class GroupHealTargetPlayer:
    """
    Nearby player hit by a group heal spell
    """
    _byte_size: int = 0
    _player_id: int
    _hp_percentage: int
    _hp: int

    def __init__(self, *, player_id: int, hp_percentage: int, hp: int):
        """
        Create a new instance of GroupHealTargetPlayer.

        Args:
            player_id (int): (Value range is 0-64008.)
            hp_percentage (int): (Value range is 0-252.)
            hp (int): (Value range is 0-64008.)
        """
        self._player_id = player_id
        self._hp_percentage = hp_percentage
        self._hp = hp

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def player_id(self) -> int:
        return self._player_id

    @property
    def hp_percentage(self) -> int:
        return self._hp_percentage

    @property
    def hp(self) -> int:
        return self._hp

    @staticmethod
    def serialize(writer: EoWriter, data: "GroupHealTargetPlayer") -> None:
        """
        Serializes an instance of `GroupHealTargetPlayer` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (GroupHealTargetPlayer): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._player_id is None:
                raise SerializationError("player_id must be provided.")
            writer.add_short(data._player_id)
            if data._hp_percentage is None:
                raise SerializationError("hp_percentage must be provided.")
            writer.add_char(data._hp_percentage)
            if data._hp is None:
                raise SerializationError("hp must be provided.")
            writer.add_short(data._hp)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "GroupHealTargetPlayer":
        """
        Deserializes an instance of `GroupHealTargetPlayer` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            GroupHealTargetPlayer: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            player_id = reader.get_short()
            hp_percentage = reader.get_char()
            hp = reader.get_short()
            result = GroupHealTargetPlayer(player_id=player_id, hp_percentage=hp_percentage, hp=hp)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"GroupHealTargetPlayer(byte_size={repr(self._byte_size)}, player_id={repr(self._player_id)}, hp_percentage={repr(self._hp_percentage)}, hp={repr(self._hp)})"
