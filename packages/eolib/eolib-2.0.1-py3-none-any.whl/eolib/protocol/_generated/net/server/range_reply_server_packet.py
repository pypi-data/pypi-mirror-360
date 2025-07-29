# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from .nearby_info import NearbyInfo
from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class RangeReplyServerPacket(Packet):
    """
    Reply to request for information about nearby players and NPCs
    """
    _byte_size: int = 0
    _nearby: NearbyInfo

    def __init__(self, *, nearby: NearbyInfo):
        """
        Create a new instance of RangeReplyServerPacket.

        Args:
            nearby (NearbyInfo): 
        """
        self._nearby = nearby

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def nearby(self) -> NearbyInfo:
        return self._nearby

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.Range

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
        RangeReplyServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "RangeReplyServerPacket") -> None:
        """
        Serializes an instance of `RangeReplyServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (RangeReplyServerPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._nearby is None:
                raise SerializationError("nearby must be provided.")
            NearbyInfo.serialize(writer, data._nearby)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "RangeReplyServerPacket":
        """
        Deserializes an instance of `RangeReplyServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            RangeReplyServerPacket: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            nearby = NearbyInfo.deserialize(reader)
            result = RangeReplyServerPacket(nearby=nearby)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"RangeReplyServerPacket(byte_size={repr(self._byte_size)}, nearby={repr(self._nearby)})"
