# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from ...direction import Direction
from ...coords import Coords
from ....serialization_error import SerializationError
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class NpcUpdatePosition:
    """
    An NPC walking
    """
    _byte_size: int = 0
    _npc_index: int
    _coords: Coords
    _direction: Direction

    def __init__(self, *, npc_index: int, coords: Coords, direction: Direction):
        """
        Create a new instance of NpcUpdatePosition.

        Args:
            npc_index (int): (Value range is 0-252.)
            coords (Coords): 
            direction (Direction): 
        """
        self._npc_index = npc_index
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
    def npc_index(self) -> int:
        return self._npc_index

    @property
    def coords(self) -> Coords:
        return self._coords

    @property
    def direction(self) -> Direction:
        return self._direction

    @staticmethod
    def serialize(writer: EoWriter, data: "NpcUpdatePosition") -> None:
        """
        Serializes an instance of `NpcUpdatePosition` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (NpcUpdatePosition): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._npc_index is None:
                raise SerializationError("npc_index must be provided.")
            writer.add_char(data._npc_index)
            if data._coords is None:
                raise SerializationError("coords must be provided.")
            Coords.serialize(writer, data._coords)
            if data._direction is None:
                raise SerializationError("direction must be provided.")
            writer.add_char(int(data._direction))
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "NpcUpdatePosition":
        """
        Deserializes an instance of `NpcUpdatePosition` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            NpcUpdatePosition: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            npc_index = reader.get_char()
            coords = Coords.deserialize(reader)
            direction = Direction(reader.get_char())
            result = NpcUpdatePosition(npc_index=npc_index, coords=coords, direction=direction)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"NpcUpdatePosition(byte_size={repr(self._byte_size)}, npc_index={repr(self._npc_index)}, coords={repr(self._coords)}, direction={repr(self._direction)})"
