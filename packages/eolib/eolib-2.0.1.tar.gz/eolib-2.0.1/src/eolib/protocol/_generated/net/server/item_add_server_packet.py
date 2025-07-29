# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ...coords import Coords
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class ItemAddServerPacket(Packet):
    """
    Item appeared on the ground
    """
    _byte_size: int = 0
    _item_id: int
    _item_index: int
    _item_amount: int
    _coords: Coords

    def __init__(self, *, item_id: int, item_index: int, item_amount: int, coords: Coords):
        """
        Create a new instance of ItemAddServerPacket.

        Args:
            item_id (int): (Value range is 0-64008.)
            item_index (int): (Value range is 0-64008.)
            item_amount (int): (Value range is 0-16194276.)
            coords (Coords): 
        """
        self._item_id = item_id
        self._item_index = item_index
        self._item_amount = item_amount
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
    def item_id(self) -> int:
        return self._item_id

    @property
    def item_index(self) -> int:
        return self._item_index

    @property
    def item_amount(self) -> int:
        return self._item_amount

    @property
    def coords(self) -> Coords:
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
        return PacketAction.Add

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        ItemAddServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "ItemAddServerPacket") -> None:
        """
        Serializes an instance of `ItemAddServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (ItemAddServerPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._item_id is None:
                raise SerializationError("item_id must be provided.")
            writer.add_short(data._item_id)
            if data._item_index is None:
                raise SerializationError("item_index must be provided.")
            writer.add_short(data._item_index)
            if data._item_amount is None:
                raise SerializationError("item_amount must be provided.")
            writer.add_three(data._item_amount)
            if data._coords is None:
                raise SerializationError("coords must be provided.")
            Coords.serialize(writer, data._coords)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "ItemAddServerPacket":
        """
        Deserializes an instance of `ItemAddServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            ItemAddServerPacket: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            item_id = reader.get_short()
            item_index = reader.get_short()
            item_amount = reader.get_three()
            coords = Coords.deserialize(reader)
            result = ItemAddServerPacket(item_id=item_id, item_index=item_index, item_amount=item_amount, coords=coords)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"ItemAddServerPacket(byte_size={repr(self._byte_size)}, item_id={repr(self._item_id)}, item_index={repr(self._item_index)}, item_amount={repr(self._item_amount)}, coords={repr(self._coords)})"
