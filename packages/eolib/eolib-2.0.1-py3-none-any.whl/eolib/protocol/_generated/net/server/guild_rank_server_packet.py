# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from __future__ import annotations
from collections.abc import Iterable
from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class GuildRankServerPacket(Packet):
    """
    Get guild rank list reply
    """
    _byte_size: int = 0
    _ranks: tuple[str, ...]

    def __init__(self, *, ranks: Iterable[str]):
        """
        Create a new instance of GuildRankServerPacket.

        Args:
            ranks (Iterable[str]): (Length must be `9`.)
        """
        self._ranks = tuple(ranks)

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def ranks(self) -> tuple[str, ...]:
        return self._ranks

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.Guild

    @staticmethod
    def action() -> PacketAction:
        """
        Returns the packet action associated with this packet.

        Returns:
            PacketAction: The packet action associated with this packet.
        """
        return PacketAction.Rank

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        GuildRankServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "GuildRankServerPacket") -> None:
        """
        Serializes an instance of `GuildRankServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (GuildRankServerPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            writer.string_sanitization_mode = True
            if data._ranks is None:
                raise SerializationError("ranks must be provided.")
            if len(data._ranks) != 9:
                raise SerializationError(f"Expected length of ranks to be exactly 9, got {len(data._ranks)}.")
            for i in range(9):
                writer.add_string(data._ranks[i])
                writer.add_byte(0xFF)
            writer.string_sanitization_mode = False
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "GuildRankServerPacket":
        """
        Deserializes an instance of `GuildRankServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            GuildRankServerPacket: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            reader.chunked_reading_mode = True
            ranks = []
            for i in range(9):
                ranks.append(reader.get_string())
                reader.next_chunk()
            reader.chunked_reading_mode = False
            result = GuildRankServerPacket(ranks=ranks)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"GuildRankServerPacket(byte_size={repr(self._byte_size)}, ranks={repr(self._ranks)})"
