# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from ...serialization_error import SerializationError
from ....data.eo_writer import EoWriter
from ....data.eo_reader import EoReader

class Spell:
    """
    A spell known by the player
    """
    _byte_size: int = 0
    _id: int
    _level: int

    def __init__(self, *, id: int, level: int):
        """
        Create a new instance of Spell.

        Args:
            id (int): (Value range is 0-64008.)
            level (int): (Value range is 0-64008.)
        """
        self._id = id
        self._level = level

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def id(self) -> int:
        return self._id

    @property
    def level(self) -> int:
        return self._level

    @staticmethod
    def serialize(writer: EoWriter, data: "Spell") -> None:
        """
        Serializes an instance of `Spell` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (Spell): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._id is None:
                raise SerializationError("id must be provided.")
            writer.add_short(data._id)
            if data._level is None:
                raise SerializationError("level must be provided.")
            writer.add_short(data._level)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "Spell":
        """
        Deserializes an instance of `Spell` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            Spell: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            id = reader.get_short()
            level = reader.get_short()
            result = Spell(id=id, level=level)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"Spell(byte_size={repr(self._byte_size)}, id={repr(self._id)}, level={repr(self._level)})"
