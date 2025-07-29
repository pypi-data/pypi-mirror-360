# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from ..weight import Weight
from ..three_item import ThreeItem
from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ...coords import Coords
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class ItemDropServerPacket(Packet):
    """
    Reply to dropping items on the ground
    """
    _byte_size: int = 0
    _dropped_item: ThreeItem
    _remaining_amount: int
    _item_index: int
    _coords: Coords
    _weight: Weight

    def __init__(self, *, dropped_item: ThreeItem, remaining_amount: int, item_index: int, coords: Coords, weight: Weight):
        """
        Create a new instance of ItemDropServerPacket.

        Args:
            dropped_item (ThreeItem): 
            remaining_amount (int): (Value range is 0-4097152080.)
            item_index (int): (Value range is 0-64008.)
            coords (Coords): 
            weight (Weight): 
        """
        self._dropped_item = dropped_item
        self._remaining_amount = remaining_amount
        self._item_index = item_index
        self._coords = coords
        self._weight = weight

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def dropped_item(self) -> ThreeItem:
        return self._dropped_item

    @property
    def remaining_amount(self) -> int:
        return self._remaining_amount

    @property
    def item_index(self) -> int:
        return self._item_index

    @property
    def coords(self) -> Coords:
        return self._coords

    @property
    def weight(self) -> Weight:
        return self._weight

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.Item

    @staticmethod
    def action() -> PacketAction:
        """
        Returns the packet action associated with this packet.

        Returns:
            PacketAction: The packet action associated with this packet.
        """
        return PacketAction.Drop

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        ItemDropServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "ItemDropServerPacket") -> None:
        """
        Serializes an instance of `ItemDropServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (ItemDropServerPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._dropped_item is None:
                raise SerializationError("dropped_item must be provided.")
            ThreeItem.serialize(writer, data._dropped_item)
            if data._remaining_amount is None:
                raise SerializationError("remaining_amount must be provided.")
            writer.add_int(data._remaining_amount)
            if data._item_index is None:
                raise SerializationError("item_index must be provided.")
            writer.add_short(data._item_index)
            if data._coords is None:
                raise SerializationError("coords must be provided.")
            Coords.serialize(writer, data._coords)
            if data._weight is None:
                raise SerializationError("weight must be provided.")
            Weight.serialize(writer, data._weight)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "ItemDropServerPacket":
        """
        Deserializes an instance of `ItemDropServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            ItemDropServerPacket: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            dropped_item = ThreeItem.deserialize(reader)
            remaining_amount = reader.get_int()
            item_index = reader.get_short()
            coords = Coords.deserialize(reader)
            weight = Weight.deserialize(reader)
            result = ItemDropServerPacket(dropped_item=dropped_item, remaining_amount=remaining_amount, item_index=item_index, coords=coords, weight=weight)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"ItemDropServerPacket(byte_size={repr(self._byte_size)}, dropped_item={repr(self._dropped_item)}, remaining_amount={repr(self._remaining_amount)}, item_index={repr(self._item_index)}, coords={repr(self._coords)}, weight={repr(self._weight)})"
