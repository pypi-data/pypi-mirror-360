# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from __future__ import annotations
from collections.abc import Iterable
from ..three_item import ThreeItem
from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ...coords import Coords
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class ChestOpenServerPacket(Packet):
    """
    Reply to opening a chest
    """
    _byte_size: int = 0
    _coords: Coords
    _items: tuple[ThreeItem, ...]

    def __init__(self, *, coords: Coords, items: Iterable[ThreeItem]):
        """
        Create a new instance of ChestOpenServerPacket.

        Args:
            coords (Coords): 
            items (Iterable[ThreeItem]): 
        """
        self._coords = coords
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
    def coords(self) -> Coords:
        return self._coords

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
        return PacketAction.Open

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        ChestOpenServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "ChestOpenServerPacket") -> None:
        """
        Serializes an instance of `ChestOpenServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (ChestOpenServerPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._coords is None:
                raise SerializationError("coords must be provided.")
            Coords.serialize(writer, data._coords)
            if data._items is None:
                raise SerializationError("items must be provided.")
            for i in range(len(data._items)):
                ThreeItem.serialize(writer, data._items[i])
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "ChestOpenServerPacket":
        """
        Deserializes an instance of `ChestOpenServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            ChestOpenServerPacket: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            coords = Coords.deserialize(reader)
            items_length = int(reader.remaining / 5)
            items = []
            for i in range(items_length):
                items.append(ThreeItem.deserialize(reader))
            result = ChestOpenServerPacket(coords=coords, items=items)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"ChestOpenServerPacket(byte_size={repr(self._byte_size)}, coords={repr(self._coords)}, items={repr(self._items)})"
