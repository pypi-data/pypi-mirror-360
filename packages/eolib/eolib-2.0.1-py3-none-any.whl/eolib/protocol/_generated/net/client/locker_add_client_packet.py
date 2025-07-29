# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from ..three_item import ThreeItem
from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ...coords import Coords
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class LockerAddClientPacket(Packet):
    """
    Adding an item to a bank locker
    """
    _byte_size: int = 0
    _locker_coords: Coords
    _deposit_item: ThreeItem

    def __init__(self, *, locker_coords: Coords, deposit_item: ThreeItem):
        """
        Create a new instance of LockerAddClientPacket.

        Args:
            locker_coords (Coords): 
            deposit_item (ThreeItem): 
        """
        self._locker_coords = locker_coords
        self._deposit_item = deposit_item

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def locker_coords(self) -> Coords:
        return self._locker_coords

    @property
    def deposit_item(self) -> ThreeItem:
        return self._deposit_item

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.Locker

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
        LockerAddClientPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "LockerAddClientPacket") -> None:
        """
        Serializes an instance of `LockerAddClientPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (LockerAddClientPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._locker_coords is None:
                raise SerializationError("locker_coords must be provided.")
            Coords.serialize(writer, data._locker_coords)
            if data._deposit_item is None:
                raise SerializationError("deposit_item must be provided.")
            ThreeItem.serialize(writer, data._deposit_item)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "LockerAddClientPacket":
        """
        Deserializes an instance of `LockerAddClientPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            LockerAddClientPacket: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            locker_coords = Coords.deserialize(reader)
            deposit_item = ThreeItem.deserialize(reader)
            result = LockerAddClientPacket(locker_coords=locker_coords, deposit_item=deposit_item)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"LockerAddClientPacket(byte_size={repr(self._byte_size)}, locker_coords={repr(self._locker_coords)}, deposit_item={repr(self._deposit_item)})"
