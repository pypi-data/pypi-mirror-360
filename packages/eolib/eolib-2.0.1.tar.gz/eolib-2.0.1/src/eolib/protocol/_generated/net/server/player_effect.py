# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from ....serialization_error import SerializationError
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class PlayerEffect:
    """
    An effect playing on a player
    """
    _byte_size: int = 0
    _player_id: int
    _effect_id: int

    def __init__(self, *, player_id: int, effect_id: int):
        """
        Create a new instance of PlayerEffect.

        Args:
            player_id (int): (Value range is 0-64008.)
            effect_id (int): (Value range is 0-16194276.)
        """
        self._player_id = player_id
        self._effect_id = effect_id

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
    def effect_id(self) -> int:
        return self._effect_id

    @staticmethod
    def serialize(writer: EoWriter, data: "PlayerEffect") -> None:
        """
        Serializes an instance of `PlayerEffect` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (PlayerEffect): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._player_id is None:
                raise SerializationError("player_id must be provided.")
            writer.add_short(data._player_id)
            if data._effect_id is None:
                raise SerializationError("effect_id must be provided.")
            writer.add_three(data._effect_id)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "PlayerEffect":
        """
        Deserializes an instance of `PlayerEffect` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            PlayerEffect: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            player_id = reader.get_short()
            effect_id = reader.get_three()
            result = PlayerEffect(player_id=player_id, effect_id=effect_id)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"PlayerEffect(byte_size={repr(self._byte_size)}, player_id={repr(self._player_id)}, effect_id={repr(self._effect_id)})"
