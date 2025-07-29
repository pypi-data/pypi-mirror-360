# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from ..weight import Weight
from ..three_item import ThreeItem
from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class ItemGetServerPacket(Packet):
    """
    Reply to taking items from the ground
    """
    _byte_size: int = 0
    _taken_item_index: int
    _taken_item: ThreeItem
    _weight: Weight

    def __init__(self, *, taken_item_index: int, taken_item: ThreeItem, weight: Weight):
        """
        Create a new instance of ItemGetServerPacket.

        Args:
            taken_item_index (int): (Value range is 0-64008.)
            taken_item (ThreeItem): 
            weight (Weight): 
        """
        self._taken_item_index = taken_item_index
        self._taken_item = taken_item
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
    def taken_item_index(self) -> int:
        return self._taken_item_index

    @property
    def taken_item(self) -> ThreeItem:
        return self._taken_item

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
        return PacketAction.Get

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        ItemGetServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "ItemGetServerPacket") -> None:
        """
        Serializes an instance of `ItemGetServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (ItemGetServerPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._taken_item_index is None:
                raise SerializationError("taken_item_index must be provided.")
            writer.add_short(data._taken_item_index)
            if data._taken_item is None:
                raise SerializationError("taken_item must be provided.")
            ThreeItem.serialize(writer, data._taken_item)
            if data._weight is None:
                raise SerializationError("weight must be provided.")
            Weight.serialize(writer, data._weight)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "ItemGetServerPacket":
        """
        Deserializes an instance of `ItemGetServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            ItemGetServerPacket: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            taken_item_index = reader.get_short()
            taken_item = ThreeItem.deserialize(reader)
            weight = Weight.deserialize(reader)
            result = ItemGetServerPacket(taken_item_index=taken_item_index, taken_item=taken_item, weight=weight)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"ItemGetServerPacket(byte_size={repr(self._byte_size)}, taken_item_index={repr(self._taken_item_index)}, taken_item={repr(self._taken_item)}, weight={repr(self._weight)})"
