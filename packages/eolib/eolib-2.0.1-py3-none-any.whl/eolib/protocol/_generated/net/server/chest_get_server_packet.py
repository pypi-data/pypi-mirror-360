# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from __future__ import annotations
from collections.abc import Iterable
from ..weight import Weight
from ..three_item import ThreeItem
from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class ChestGetServerPacket(Packet):
    """
    Reply to removing an item from a chest
    """
    _byte_size: int = 0
    _taken_item: ThreeItem
    _weight: Weight
    _items: tuple[ThreeItem, ...]

    def __init__(self, *, taken_item: ThreeItem, weight: Weight, items: Iterable[ThreeItem]):
        """
        Create a new instance of ChestGetServerPacket.

        Args:
            taken_item (ThreeItem): 
            weight (Weight): 
            items (Iterable[ThreeItem]): 
        """
        self._taken_item = taken_item
        self._weight = weight
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
    def taken_item(self) -> ThreeItem:
        return self._taken_item

    @property
    def weight(self) -> Weight:
        return self._weight

    @property
    def items(self) -> tuple[ThreeItem, ...]:
        return self._items

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.Chest

    @staticmethod
    def action() -> PacketAction:
        """
        Returns the packet action associated with this packet.

        Returns:
            PacketAction: The packet action associated with this packet.
        """
        return PacketAction.Get

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        ChestGetServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "ChestGetServerPacket") -> None:
        """
        Serializes an instance of `ChestGetServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (ChestGetServerPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._taken_item is None:
                raise SerializationError("taken_item must be provided.")
            ThreeItem.serialize(writer, data._taken_item)
            if data._weight is None:
                raise SerializationError("weight must be provided.")
            Weight.serialize(writer, data._weight)
            if data._items is None:
                raise SerializationError("items must be provided.")
            for i in range(len(data._items)):
                ThreeItem.serialize(writer, data._items[i])
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "ChestGetServerPacket":
        """
        Deserializes an instance of `ChestGetServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            ChestGetServerPacket: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            taken_item = ThreeItem.deserialize(reader)
            weight = Weight.deserialize(reader)
            items_length = int(reader.remaining / 5)
            items = []
            for i in range(items_length):
                items.append(ThreeItem.deserialize(reader))
            result = ChestGetServerPacket(taken_item=taken_item, weight=weight, items=items)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"ChestGetServerPacket(byte_size={repr(self._byte_size)}, taken_item={repr(self._taken_item)}, weight={repr(self._weight)}, items={repr(self._items)})"
