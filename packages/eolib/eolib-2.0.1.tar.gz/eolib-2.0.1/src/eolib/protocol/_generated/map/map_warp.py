# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from ..coords import Coords
from ...serialization_error import SerializationError
from ....data.eo_writer import EoWriter
from ....data.eo_reader import EoReader

class MapWarp:
    """
    Warp EMF entity
    """
    _byte_size: int = 0
    _destination_map: int
    _destination_coords: Coords
    _level_required: int
    _door: int

    def __init__(self, *, destination_map: int, destination_coords: Coords, level_required: int, door: int):
        """
        Create a new instance of MapWarp.

        Args:
            destination_map (int): (Value range is 0-64008.)
            destination_coords (Coords): 
            level_required (int): (Value range is 0-252.)
            door (int): (Value range is 0-64008.)
        """
        self._destination_map = destination_map
        self._destination_coords = destination_coords
        self._level_required = level_required
        self._door = door

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def destination_map(self) -> int:
        return self._destination_map

    @property
    def destination_coords(self) -> Coords:
        return self._destination_coords

    @property
    def level_required(self) -> int:
        return self._level_required

    @property
    def door(self) -> int:
        return self._door

    @staticmethod
    def serialize(writer: EoWriter, data: "MapWarp") -> None:
        """
        Serializes an instance of `MapWarp` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (MapWarp): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._destination_map is None:
                raise SerializationError("destination_map must be provided.")
            writer.add_short(data._destination_map)
            if data._destination_coords is None:
                raise SerializationError("destination_coords must be provided.")
            Coords.serialize(writer, data._destination_coords)
            if data._level_required is None:
                raise SerializationError("level_required must be provided.")
            writer.add_char(data._level_required)
            if data._door is None:
                raise SerializationError("door must be provided.")
            writer.add_short(data._door)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "MapWarp":
        """
        Deserializes an instance of `MapWarp` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            MapWarp: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            destination_map = reader.get_short()
            destination_coords = Coords.deserialize(reader)
            level_required = reader.get_char()
            door = reader.get_short()
            result = MapWarp(destination_map=destination_map, destination_coords=destination_coords, level_required=level_required, door=door)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"MapWarp(byte_size={repr(self._byte_size)}, destination_map={repr(self._destination_map)}, destination_coords={repr(self._destination_coords)}, level_required={repr(self._level_required)}, door={repr(self._door)})"
