# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from ...coords import Coords
from ....serialization_error import SerializationError
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class TileEffect:
    """
    An effect playing on a tile
    """
    _byte_size: int = 0
    _coords: Coords
    _effect_id: int

    def __init__(self, *, coords: Coords, effect_id: int):
        """
        Create a new instance of TileEffect.

        Args:
            coords (Coords): 
            effect_id (int): (Value range is 0-64008.)
        """
        self._coords = coords
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
    def coords(self) -> Coords:
        return self._coords

    @property
    def effect_id(self) -> int:
        return self._effect_id

    @staticmethod
    def serialize(writer: EoWriter, data: "TileEffect") -> None:
        """
        Serializes an instance of `TileEffect` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (TileEffect): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._coords is None:
                raise SerializationError("coords must be provided.")
            Coords.serialize(writer, data._coords)
            if data._effect_id is None:
                raise SerializationError("effect_id must be provided.")
            writer.add_short(data._effect_id)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "TileEffect":
        """
        Deserializes an instance of `TileEffect` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            TileEffect: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            coords = Coords.deserialize(reader)
            effect_id = reader.get_short()
            result = TileEffect(coords=coords, effect_id=effect_id)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"TileEffect(byte_size={repr(self._byte_size)}, coords={repr(self._coords)}, effect_id={repr(self._effect_id)})"
