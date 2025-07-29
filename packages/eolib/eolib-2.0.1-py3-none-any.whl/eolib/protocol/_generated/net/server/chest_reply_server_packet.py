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

class ChestReplyServerPacket(Packet):
    """
    Reply to placing an item in to a chest
    """
    _byte_size: int = 0
    _added_item_id: int
    _remaining_amount: int
    _weight: Weight
    _items: tuple[ThreeItem, ...]

    def __init__(self, *, added_item_id: int, remaining_amount: int, weight: Weight, items: Iterable[ThreeItem]):
        """
        Create a new instance of ChestReplyServerPacket.

        Args:
            added_item_id (int): (Value range is 0-64008.)
            remaining_amount (int): (Value range is 0-4097152080.)
            weight (Weight): 
            items (Iterable[ThreeItem]): 
        """
        self._added_item_id = added_item_id
        self._remaining_amount = remaining_amount
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
    def added_item_id(self) -> int:
        return self._added_item_id

    @property
    def remaining_amount(self) -> int:
        return self._remaining_amount

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
        return PacketAction.Reply

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        ChestReplyServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "ChestReplyServerPacket") -> None:
        """
        Serializes an instance of `ChestReplyServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (ChestReplyServerPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._added_item_id is None:
                raise SerializationError("added_item_id must be provided.")
            writer.add_short(data._added_item_id)
            if data._remaining_amount is None:
                raise SerializationError("remaining_amount must be provided.")
            writer.add_int(data._remaining_amount)
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
    def deserialize(reader: EoReader) -> "ChestReplyServerPacket":
        """
        Deserializes an instance of `ChestReplyServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            ChestReplyServerPacket: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            added_item_id = reader.get_short()
            remaining_amount = reader.get_int()
            weight = Weight.deserialize(reader)
            items_length = int(reader.remaining / 5)
            items = []
            for i in range(items_length):
                items.append(ThreeItem.deserialize(reader))
            result = ChestReplyServerPacket(added_item_id=added_item_id, remaining_amount=remaining_amount, weight=weight, items=items)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"ChestReplyServerPacket(byte_size={repr(self._byte_size)}, added_item_id={repr(self._added_item_id)}, remaining_amount={repr(self._remaining_amount)}, weight={repr(self._weight)}, items={repr(self._items)})"
