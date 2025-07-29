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

class ItemKickServerPacket(Packet):
    """
    Lose item (from quest)
    """
    _byte_size: int = 0
    _item: Item
    _current_weight: int

    def __init__(self, *, item: Item, current_weight: int):
        """
        Create a new instance of ItemKickServerPacket.

        Args:
            item (Item): 
            current_weight (int): (Value range is 0-252.)
        """
        self._item = item
        self._current_weight = current_weight

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def item(self) -> Item:
        return self._item

    @property
    def current_weight(self) -> int:
        return self._current_weight

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
        return PacketAction.Kick

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        ItemKickServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "ItemKickServerPacket") -> None:
        """
        Serializes an instance of `ItemKickServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (ItemKickServerPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._item is None:
                raise SerializationError("item must be provided.")
            Item.serialize(writer, data._item)
            if data._current_weight is None:
                raise SerializationError("current_weight must be provided.")
            writer.add_char(data._current_weight)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "ItemKickServerPacket":
        """
        Deserializes an instance of `ItemKickServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            ItemKickServerPacket: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            item = Item.deserialize(reader)
            current_weight = reader.get_char()
            result = ItemKickServerPacket(item=item, current_weight=current_weight)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"ItemKickServerPacket(byte_size={repr(self._byte_size)}, item={repr(self._item)}, current_weight={repr(self._current_weight)})"
