# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from ...direction import Direction
from ...coords import Coords
from ....serialization_error import SerializationError
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class WalkAction:
    """
    Common data between walk packets
    """
    _byte_size: int = 0
    _direction: Direction
    _timestamp: int
    _coords: Coords

    def __init__(self, *, direction: Direction, timestamp: int, coords: Coords):
        """
        Create a new instance of WalkAction.

        Args:
            direction (Direction): 
            timestamp (int): (Value range is 0-16194276.)
            coords (Coords): 
        """
        self._direction = direction
        self._timestamp = timestamp
        self._coords = coords

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def direction(self) -> Direction:
        return self._direction

    @property
    def timestamp(self) -> int:
        return self._timestamp

    @property
    def coords(self) -> Coords:
        return self._coords

    @staticmethod
    def serialize(writer: EoWriter, data: "WalkAction") -> None:
        """
        Serializes an instance of `WalkAction` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (WalkAction): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._direction is None:
                raise SerializationError("direction must be provided.")
            writer.add_char(int(data._direction))
            if data._timestamp is None:
                raise SerializationError("timestamp must be provided.")
            writer.add_three(data._timestamp)
            if data._coords is None:
                raise SerializationError("coords must be provided.")
            Coords.serialize(writer, data._coords)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "WalkAction":
        """
        Deserializes an instance of `WalkAction` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            WalkAction: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            direction = Direction(reader.get_char())
            timestamp = reader.get_three()
            coords = Coords.deserialize(reader)
            result = WalkAction(direction=direction, timestamp=timestamp, coords=coords)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"WalkAction(byte_size={repr(self._byte_size)}, direction={repr(self._direction)}, timestamp={repr(self._timestamp)}, coords={repr(self._coords)})"
