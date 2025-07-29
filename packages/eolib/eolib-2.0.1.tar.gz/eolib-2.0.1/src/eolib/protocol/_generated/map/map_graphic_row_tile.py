# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from ...serialization_error import SerializationError
from ....data.eo_writer import EoWriter
from ....data.eo_reader import EoReader

class MapGraphicRowTile:
    """
    A single tile in a row of map graphics
    """
    _byte_size: int = 0
    _x: int
    _graphic: int

    def __init__(self, *, x: int, graphic: int):
        """
        Create a new instance of MapGraphicRowTile.

        Args:
            x (int): (Value range is 0-252.)
            graphic (int): (Value range is 0-64008.)
        """
        self._x = x
        self._graphic = graphic

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
    def graphic(self) -> int:
        return self._graphic

    @staticmethod
    def serialize(writer: EoWriter, data: "MapGraphicRowTile") -> None:
        """
        Serializes an instance of `MapGraphicRowTile` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (MapGraphicRowTile): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._x is None:
                raise SerializationError("x must be provided.")
            writer.add_char(data._x)
            if data._graphic is None:
                raise SerializationError("graphic must be provided.")
            writer.add_short(data._graphic)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "MapGraphicRowTile":
        """
        Deserializes an instance of `MapGraphicRowTile` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            MapGraphicRowTile: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            x = reader.get_char()
            graphic = reader.get_short()
            result = MapGraphicRowTile(x=x, graphic=graphic)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"MapGraphicRowTile(byte_size={repr(self._byte_size)}, x={repr(self._x)}, graphic={repr(self._graphic)})"
