# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from .byte_coords import ByteCoords
from ..three_item import ThreeItem
from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class ItemDropClientPacket(Packet):
    """
    Dropping items on the ground
    """
    _byte_size: int = 0
    _item: ThreeItem
    _coords: ByteCoords

    def __init__(self, *, item: ThreeItem, coords: ByteCoords):
        """
        Create a new instance of ItemDropClientPacket.

        Args:
            item (ThreeItem): 
            coords (ByteCoords): The official client sends 255 byte values for the coords if an item is dropped via the GUI button. 255 values here should be interpreted to mean "drop at current coords". Otherwise, the x and y fields contain encoded numbers that must be explicitly decoded to get the actual x and y values.
        """
        self._item = item
        self._coords = coords

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def item(self) -> ThreeItem:
        return self._item

    @property
    def coords(self) -> ByteCoords:
        """
        The official client sends 255 byte values for the coords if an item is dropped via
        the GUI button.
        255 values here should be interpreted to mean "drop at current coords".
        Otherwise, the x and y fields contain encoded numbers that must be explicitly
        decoded to get the actual x and y values.
        """
        return self._coords

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
        ItemDropClientPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "ItemDropClientPacket") -> None:
        """
        Serializes an instance of `ItemDropClientPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (ItemDropClientPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._item is None:
                raise SerializationError("item must be provided.")
            ThreeItem.serialize(writer, data._item)
            if data._coords is None:
                raise SerializationError("coords must be provided.")
            ByteCoords.serialize(writer, data._coords)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "ItemDropClientPacket":
        """
        Deserializes an instance of `ItemDropClientPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            ItemDropClientPacket: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            item = ThreeItem.deserialize(reader)
            coords = ByteCoords.deserialize(reader)
            result = ItemDropClientPacket(item=item, coords=coords)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"ItemDropClientPacket(byte_size={repr(self._byte_size)}, item={repr(self._item)}, coords={repr(self._coords)})"
