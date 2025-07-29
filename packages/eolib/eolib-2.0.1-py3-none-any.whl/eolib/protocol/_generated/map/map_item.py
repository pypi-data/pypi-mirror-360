# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from ..coords import Coords
from ...serialization_error import SerializationError
from ....data.eo_writer import EoWriter
from ....data.eo_reader import EoReader

class MapItem:
    """
    Item spawn EMF entity
    """
    _byte_size: int = 0
    _coords: Coords
    _key: int
    _chest_slot: int
    _item_id: int
    _spawn_time: int
    _amount: int

    def __init__(self, *, coords: Coords, key: int, chest_slot: int, item_id: int, spawn_time: int, amount: int):
        """
        Create a new instance of MapItem.

        Args:
            coords (Coords): 
            key (int): (Value range is 0-64008.)
            chest_slot (int): (Value range is 0-252.)
            item_id (int): (Value range is 0-64008.)
            spawn_time (int): (Value range is 0-64008.)
            amount (int): (Value range is 0-16194276.)
        """
        self._coords = coords
        self._key = key
        self._chest_slot = chest_slot
        self._item_id = item_id
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
    def key(self) -> int:
        return self._key

    @property
    def chest_slot(self) -> int:
        return self._chest_slot

    @property
    def item_id(self) -> int:
        return self._item_id

    @property
    def spawn_time(self) -> int:
        return self._spawn_time

    @property
    def amount(self) -> int:
        return self._amount

    @staticmethod
    def serialize(writer: EoWriter, data: "MapItem") -> None:
        """
        Serializes an instance of `MapItem` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (MapItem): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._coords is None:
                raise SerializationError("coords must be provided.")
            Coords.serialize(writer, data._coords)
            if data._key is None:
                raise SerializationError("key must be provided.")
            writer.add_short(data._key)
            if data._chest_slot is None:
                raise SerializationError("chest_slot must be provided.")
            writer.add_char(data._chest_slot)
            if data._item_id is None:
                raise SerializationError("item_id must be provided.")
            writer.add_short(data._item_id)
            if data._spawn_time is None:
                raise SerializationError("spawn_time must be provided.")
            writer.add_short(data._spawn_time)
            if data._amount is None:
                raise SerializationError("amount must be provided.")
            writer.add_three(data._amount)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "MapItem":
        """
        Deserializes an instance of `MapItem` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            MapItem: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            coords = Coords.deserialize(reader)
            key = reader.get_short()
            chest_slot = reader.get_char()
            item_id = reader.get_short()
            spawn_time = reader.get_short()
            amount = reader.get_three()
            result = MapItem(coords=coords, key=key, chest_slot=chest_slot, item_id=item_id, spawn_time=spawn_time, amount=amount)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"MapItem(byte_size={repr(self._byte_size)}, coords={repr(self._coords)}, key={repr(self._key)}, chest_slot={repr(self._chest_slot)}, item_id={repr(self._item_id)}, spawn_time={repr(self._spawn_time)}, amount={repr(self._amount)})"
