# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from .map_warp import MapWarp
from ...serialization_error import SerializationError
from ....data.eo_writer import EoWriter
from ....data.eo_reader import EoReader

class MapWarpRowTile:
    """
    A single tile in a row of warp entities
    """
    _byte_size: int = 0
    _x: int
    _warp: MapWarp

    def __init__(self, *, x: int, warp: MapWarp):
        """
        Create a new instance of MapWarpRowTile.

        Args:
            x (int): (Value range is 0-252.)
            warp (MapWarp): 
        """
        self._x = x
        self._warp = warp

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def x(self) -> int:
        return self._x

    @property
    def warp(self) -> MapWarp:
        return self._warp

    @staticmethod
    def serialize(writer: EoWriter, data: "MapWarpRowTile") -> None:
        """
        Serializes an instance of `MapWarpRowTile` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (MapWarpRowTile): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._x is None:
                raise SerializationError("x must be provided.")
            writer.add_char(data._x)
            if data._warp is None:
                raise SerializationError("warp must be provided.")
            MapWarp.serialize(writer, data._warp)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "MapWarpRowTile":
        """
        Deserializes an instance of `MapWarpRowTile` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            MapWarpRowTile: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            x = reader.get_char()
            warp = MapWarp.deserialize(reader)
            result = MapWarpRowTile(x=x, warp=warp)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"MapWarpRowTile(byte_size={repr(self._byte_size)}, x={repr(self._x)}, warp={repr(self._warp)})"
