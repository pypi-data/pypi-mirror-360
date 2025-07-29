# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from ..coords import Coords
from ...serialization_error import SerializationError
from ....data.eo_writer import EoWriter
from ....data.eo_reader import EoReader

class MapNpc:
    """
    NPC spawn EMF entity
    """
    _byte_size: int = 0
    _coords: Coords
    _id: int
    _spawn_type: int
    _spawn_time: int
    _amount: int

    def __init__(self, *, coords: Coords, id: int, spawn_type: int, spawn_time: int, amount: int):
        """
        Create a new instance of MapNpc.

        Args:
            coords (Coords): 
            id (int): (Value range is 0-64008.)
            spawn_type (int): (Value range is 0-252.)
            spawn_time (int): (Value range is 0-64008.)
            amount (int): (Value range is 0-252.)
        """
        self._coords = coords
        self._id = id
        self._spawn_type = spawn_type
        self._spawn_time = spawn_time
        self._amount = amount

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
    def id(self) -> int:
        return self._id

    @property
    def spawn_type(self) -> int:
        return self._spawn_type

    @property
    def spawn_time(self) -> int:
        return self._spawn_time

    @property
    def amount(self) -> int:
        return self._amount

    @staticmethod
    def serialize(writer: EoWriter, data: "MapNpc") -> None:
        """
        Serializes an instance of `MapNpc` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (MapNpc): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._coords is None:
                raise SerializationError("coords must be provided.")
            Coords.serialize(writer, data._coords)
            if data._id is None:
                raise SerializationError("id must be provided.")
            writer.add_short(data._id)
            if data._spawn_type is None:
                raise SerializationError("spawn_type must be provided.")
            writer.add_char(data._spawn_type)
            if data._spawn_time is None:
                raise SerializationError("spawn_time must be provided.")
            writer.add_short(data._spawn_time)
            if data._amount is None:
                raise SerializationError("amount must be provided.")
            writer.add_char(data._amount)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "MapNpc":
        """
        Deserializes an instance of `MapNpc` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            MapNpc: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            coords = Coords.deserialize(reader)
            id = reader.get_short()
            spawn_type = reader.get_char()
            spawn_time = reader.get_short()
            amount = reader.get_char()
            result = MapNpc(coords=coords, id=id, spawn_type=spawn_type, spawn_time=spawn_time, amount=amount)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"MapNpc(byte_size={repr(self._byte_size)}, coords={repr(self._coords)}, id={repr(self._id)}, spawn_type={repr(self._spawn_type)}, spawn_time={repr(self._spawn_time)}, amount={repr(self._amount)})"
