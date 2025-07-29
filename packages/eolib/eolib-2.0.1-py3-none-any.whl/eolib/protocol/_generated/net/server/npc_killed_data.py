# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from ...direction import Direction
from ...coords import Coords
from ....serialization_error import SerializationError
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class NpcKilledData:
    """
    Information about an NPC that has been killed
    """
    _byte_size: int = 0
    _killer_id: int
    _killer_direction: Direction
    _npc_index: int
    _drop_index: int
    _drop_id: int
    _drop_coords: Coords
    _drop_amount: int
    _damage: int

    def __init__(self, *, killer_id: int, killer_direction: Direction, npc_index: int, drop_index: int, drop_id: int, drop_coords: Coords, drop_amount: int, damage: int):
        """
        Create a new instance of NpcKilledData.

        Args:
            killer_id (int): (Value range is 0-64008.)
            killer_direction (Direction): 
            npc_index (int): (Value range is 0-64008.)
            drop_index (int): (Value range is 0-64008.)
            drop_id (int): (Value range is 0-64008.)
            drop_coords (Coords): 
            drop_amount (int): (Value range is 0-4097152080.)
            damage (int): (Value range is 0-16194276.)
        """
        self._killer_id = killer_id
        self._killer_direction = killer_direction
        self._npc_index = npc_index
        self._drop_index = drop_index
        self._drop_id = drop_id
        self._drop_coords = drop_coords
        self._drop_amount = drop_amount
        self._damage = damage

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def killer_id(self) -> int:
        return self._killer_id

    @property
    def killer_direction(self) -> Direction:
        return self._killer_direction

    @property
    def npc_index(self) -> int:
        return self._npc_index

    @property
    def drop_index(self) -> int:
        return self._drop_index

    @property
    def drop_id(self) -> int:
        return self._drop_id

    @property
    def drop_coords(self) -> Coords:
        return self._drop_coords

    @property
    def drop_amount(self) -> int:
        return self._drop_amount

    @property
    def damage(self) -> int:
        return self._damage

    @staticmethod
    def serialize(writer: EoWriter, data: "NpcKilledData") -> None:
        """
        Serializes an instance of `NpcKilledData` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (NpcKilledData): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._killer_id is None:
                raise SerializationError("killer_id must be provided.")
            writer.add_short(data._killer_id)
            if data._killer_direction is None:
                raise SerializationError("killer_direction must be provided.")
            writer.add_char(int(data._killer_direction))
            if data._npc_index is None:
                raise SerializationError("npc_index must be provided.")
            writer.add_short(data._npc_index)
            if data._drop_index is None:
                raise SerializationError("drop_index must be provided.")
            writer.add_short(data._drop_index)
            if data._drop_id is None:
                raise SerializationError("drop_id must be provided.")
            writer.add_short(data._drop_id)
            if data._drop_coords is None:
                raise SerializationError("drop_coords must be provided.")
            Coords.serialize(writer, data._drop_coords)
            if data._drop_amount is None:
                raise SerializationError("drop_amount must be provided.")
            writer.add_int(data._drop_amount)
            if data._damage is None:
                raise SerializationError("damage must be provided.")
            writer.add_three(data._damage)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "NpcKilledData":
        """
        Deserializes an instance of `NpcKilledData` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            NpcKilledData: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            killer_id = reader.get_short()
            killer_direction = Direction(reader.get_char())
            npc_index = reader.get_short()
            drop_index = reader.get_short()
            drop_id = reader.get_short()
            drop_coords = Coords.deserialize(reader)
            drop_amount = reader.get_int()
            damage = reader.get_three()
            result = NpcKilledData(killer_id=killer_id, killer_direction=killer_direction, npc_index=npc_index, drop_index=drop_index, drop_id=drop_id, drop_coords=drop_coords, drop_amount=drop_amount, damage=damage)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"NpcKilledData(byte_size={repr(self._byte_size)}, killer_id={repr(self._killer_id)}, killer_direction={repr(self._killer_direction)}, npc_index={repr(self._npc_index)}, drop_index={repr(self._drop_index)}, drop_id={repr(self._drop_id)}, drop_coords={repr(self._drop_coords)}, drop_amount={repr(self._drop_amount)}, damage={repr(self._damage)})"
