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

class ItemJunkServerPacket(Packet):
    """
    Reply to junking items
    """
    _byte_size: int = 0
    _junked_item: ThreeItem
    _remaining_amount: int
    _weight: Weight

    def __init__(self, *, junked_item: ThreeItem, remaining_amount: int, weight: Weight):
        """
        Create a new instance of ItemJunkServerPacket.

        Args:
            junked_item (ThreeItem): 
            remaining_amount (int): (Value range is 0-4097152080.)
            weight (Weight): 
        """
        self._junked_item = junked_item
        self._remaining_amount = remaining_amount
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
    def junked_item(self) -> ThreeItem:
        return self._junked_item

    @property
    def remaining_amount(self) -> int:
        return self._remaining_amount

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
        return PacketAction.Junk

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        ItemJunkServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "ItemJunkServerPacket") -> None:
        """
        Serializes an instance of `ItemJunkServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (ItemJunkServerPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._junked_item is None:
                raise SerializationError("junked_item must be provided.")
            ThreeItem.serialize(writer, data._junked_item)
            if data._remaining_amount is None:
                raise SerializationError("remaining_amount must be provided.")
            writer.add_int(data._remaining_amount)
            if data._weight is None:
                raise SerializationError("weight must be provided.")
            Weight.serialize(writer, data._weight)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "ItemJunkServerPacket":
        """
        Deserializes an instance of `ItemJunkServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            ItemJunkServerPacket: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            junked_item = ThreeItem.deserialize(reader)
            remaining_amount = reader.get_int()
            weight = Weight.deserialize(reader)
            result = ItemJunkServerPacket(junked_item=junked_item, remaining_amount=remaining_amount, weight=weight)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"ItemJunkServerPacket(byte_size={repr(self._byte_size)}, junked_item={repr(self._junked_item)}, remaining_amount={repr(self._remaining_amount)}, weight={repr(self._weight)})"
