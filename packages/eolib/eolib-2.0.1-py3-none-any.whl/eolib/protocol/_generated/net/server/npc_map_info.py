# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from ...direction import Direction
from ...coords import Coords
from ....serialization_error import SerializationError
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class NpcMapInfo:
    """
    Information about a nearby NPC
    """
    _byte_size: int = 0
    _index: int
    _id: int
    _coords: Coords
    _direction: Direction

    def __init__(self, *, index: int, id: int, coords: Coords, direction: Direction):
        """
        Create a new instance of NpcMapInfo.

        Args:
            index (int): (Value range is 0-252.)
            id (int): (Value range is 0-64008.)
            coords (Coords): 
            direction (Direction): 
        """
        self._index = index
        self._id = id
        self._coords = coords
        self._direction = direction

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def index(self) -> int:
        return self._index

    @property
    def id(self) -> int:
        return self._id

    @property
    def coords(self) -> Coords:
        return self._coords

    @property
    def direction(self) -> Direction:
        return self._direction

    @staticmethod
    def serialize(writer: EoWriter, data: "NpcMapInfo") -> None:
        """
        Serializes an instance of `NpcMapInfo` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (NpcMapInfo): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._index is None:
                raise SerializationError("index must be provided.")
            writer.add_char(data._index)
            if data._id is None:
                raise SerializationError("id must be provided.")
            writer.add_short(data._id)
            if data._coords is None:
                raise SerializationError("coords must be provided.")
            Coords.serialize(writer, data._coords)
            if data._direction is None:
                raise SerializationError("direction must be provided.")
            writer.add_char(int(data._direction))
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "NpcMapInfo":
        """
        Deserializes an instance of `NpcMapInfo` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            NpcMapInfo: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            index = reader.get_char()
            id = reader.get_short()
            coords = Coords.deserialize(reader)
            direction = Direction(reader.get_char())
            result = NpcMapInfo(index=index, id=id, coords=coords, direction=direction)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"NpcMapInfo(byte_size={repr(self._byte_size)}, index={repr(self._index)}, id={repr(self._id)}, coords={repr(self._coords)}, direction={repr(self._direction)})"
