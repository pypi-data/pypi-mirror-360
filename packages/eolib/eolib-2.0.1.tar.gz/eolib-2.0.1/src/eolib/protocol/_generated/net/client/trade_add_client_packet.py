# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ..item import Item
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class TradeAddClientPacket(Packet):
    """
    Add an item to the trade screen
    """
    _byte_size: int = 0
    _add_item: Item

    def __init__(self, *, add_item: Item):
        """
        Create a new instance of TradeAddClientPacket.

        Args:
            add_item (Item): 
        """
        self._add_item = add_item

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def add_item(self) -> Item:
        return self._add_item

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.Trade

    @staticmethod
    def action() -> PacketAction:
        """
        Returns the packet action associated with this packet.

        Returns:
            PacketAction: The packet action associated with this packet.
        """
        return PacketAction.Add

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        TradeAddClientPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "TradeAddClientPacket") -> None:
        """
        Serializes an instance of `TradeAddClientPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (TradeAddClientPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._add_item is None:
                raise SerializationError("add_item must be provided.")
            Item.serialize(writer, data._add_item)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "TradeAddClientPacket":
        """
        Deserializes an instance of `TradeAddClientPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            TradeAddClientPacket: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            add_item = Item.deserialize(reader)
            result = TradeAddClientPacket(add_item=add_item)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"TradeAddClientPacket(byte_size={repr(self._byte_size)}, add_item={repr(self._add_item)})"
