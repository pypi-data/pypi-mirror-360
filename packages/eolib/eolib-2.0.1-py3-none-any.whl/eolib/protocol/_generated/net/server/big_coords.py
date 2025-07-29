# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from ....serialization_error import SerializationError
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class BigCoords:
    """
    Map coordinates with 2-byte values
    """
    _byte_size: int = 0
    _x: int
    _y: int

    def __init__(self, *, x: int, y: int):
        """
        Create a new instance of BigCoords.

        Args:
            x (int): (Value range is 0-64008.)
            y (int): (Value range is 0-64008.)
        """
        self._x = x
        self._y = y

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
    def y(self) -> int:
        return self._y

    @staticmethod
    def serialize(writer: EoWriter, data: "BigCoords") -> None:
        """
        Serializes an instance of `BigCoords` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (BigCoords): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._x is None:
                raise SerializationError("x must be provided.")
            writer.add_short(data._x)
            if data._y is None:
                raise SerializationError("y must be provided.")
            writer.add_short(data._y)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "BigCoords":
        """
        Deserializes an instance of `BigCoords` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            BigCoords: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            x = reader.get_short()
            y = reader.get_short()
            result = BigCoords(x=x, y=y)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"BigCoords(byte_size={repr(self._byte_size)}, x={repr(self._x)}, y={repr(self._y)})"
