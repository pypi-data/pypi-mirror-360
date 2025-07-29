# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from __future__ import annotations
from collections.abc import Iterable
from ..item import Item
from ....serialization_error import SerializationError
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class TradeItemData:
    """
    Trade window item data
    """
    _byte_size: int = 0
    _player_id: int
    _items: tuple[Item, ...]

    def __init__(self, *, player_id: int, items: Iterable[Item]):
        """
        Create a new instance of TradeItemData.

        Args:
            player_id (int): (Value range is 0-64008.)
            items (Iterable[Item]): 
        """
        self._player_id = player_id
        self._items = tuple(items)

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def player_id(self) -> int:
        return self._player_id

    @property
    def items(self) -> tuple[Item, ...]:
        return self._items

    @staticmethod
    def serialize(writer: EoWriter, data: "TradeItemData") -> None:
        """
        Serializes an instance of `TradeItemData` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (TradeItemData): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._player_id is None:
                raise SerializationError("player_id must be provided.")
            writer.add_short(data._player_id)
            if data._items is None:
                raise SerializationError("items must be provided.")
            for i in range(len(data._items)):
                Item.serialize(writer, data._items[i])
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "TradeItemData":
        """
        Deserializes an instance of `TradeItemData` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            TradeItemData: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            player_id = reader.get_short()
            items_length = int(reader.remaining / 6)
            items = []
            for i in range(items_length):
                items.append(Item.deserialize(reader))
            result = TradeItemData(player_id=player_id, items=items)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"TradeItemData(byte_size={repr(self._byte_size)}, player_id={repr(self._player_id)}, items={repr(self._items)})"
