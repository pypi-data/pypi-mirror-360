# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from ....serialization_error import SerializationError
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class MapDrainDamageOther:
    """
    Another player taking damage from a map HP drain
    """
    _byte_size: int = 0
    _player_id: int
    _hp_percentage: int
    _damage: int

    def __init__(self, *, player_id: int, hp_percentage: int, damage: int):
        """
        Create a new instance of MapDrainDamageOther.

        Args:
            player_id (int): (Value range is 0-64008.)
            hp_percentage (int): (Value range is 0-252.)
            damage (int): (Value range is 0-64008.)
        """
        self._player_id = player_id
        self._hp_percentage = hp_percentage
        self._damage = damage

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
    def damage(self) -> int:
        return self._damage

    @staticmethod
    def serialize(writer: EoWriter, data: "MapDrainDamageOther") -> None:
        """
        Serializes an instance of `MapDrainDamageOther` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (MapDrainDamageOther): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._player_id is None:
                raise SerializationError("player_id must be provided.")
            writer.add_short(data._player_id)
            if data._hp_percentage is None:
                raise SerializationError("hp_percentage must be provided.")
            writer.add_char(data._hp_percentage)
            if data._damage is None:
                raise SerializationError("damage must be provided.")
            writer.add_short(data._damage)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "MapDrainDamageOther":
        """
        Deserializes an instance of `MapDrainDamageOther` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            MapDrainDamageOther: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            player_id = reader.get_short()
            hp_percentage = reader.get_char()
            damage = reader.get_short()
            result = MapDrainDamageOther(player_id=player_id, hp_percentage=hp_percentage, damage=damage)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"MapDrainDamageOther(byte_size={repr(self._byte_size)}, player_id={repr(self._player_id)}, hp_percentage={repr(self._hp_percentage)}, damage={repr(self._damage)})"
