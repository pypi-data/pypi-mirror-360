# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class ArenaUseServerPacket(Packet):
    """
    Arena start message
    """
    _byte_size: int = 0
    _players_count: int

    def __init__(self, *, players_count: int):
        """
        Create a new instance of ArenaUseServerPacket.

        Args:
            players_count (int): (Value range is 0-252.)
        """
        self._players_count = players_count

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def players_count(self) -> int:
        return self._players_count

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.Arena

    @staticmethod
    def action() -> PacketAction:
        """
        Returns the packet action associated with this packet.

        Returns:
            PacketAction: The packet action associated with this packet.
        """
        return PacketAction.Use

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        ArenaUseServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "ArenaUseServerPacket") -> None:
        """
        Serializes an instance of `ArenaUseServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (ArenaUseServerPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._players_count is None:
                raise SerializationError("players_count must be provided.")
            writer.add_char(data._players_count)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "ArenaUseServerPacket":
        """
        Deserializes an instance of `ArenaUseServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            ArenaUseServerPacket: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            players_count = reader.get_char()
            result = ArenaUseServerPacket(players_count=players_count)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"ArenaUseServerPacket(byte_size={repr(self._byte_size)}, players_count={repr(self._players_count)})"
