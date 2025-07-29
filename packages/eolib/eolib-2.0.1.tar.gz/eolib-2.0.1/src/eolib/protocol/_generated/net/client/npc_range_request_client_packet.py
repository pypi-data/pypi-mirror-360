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

class NpcRangeRequestClientPacket(Packet):
    """
    Requesting info about nearby NPCs
    """
    _byte_size: int = 0
    _npc_indexes_length: int
    _npc_indexes: tuple[int, ...]

    def __init__(self, *, npc_indexes: Iterable[int]):
        """
        Create a new instance of NpcRangeRequestClientPacket.

        Args:
            npc_indexes (Iterable[int]): (Length must be 252 or less.) (Element value range is 0-252.)
        """
        self._npc_indexes = tuple(npc_indexes)
        self._npc_indexes_length = len(self._npc_indexes)

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def npc_indexes(self) -> tuple[int, ...]:
        return self._npc_indexes

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.NpcRange

    @staticmethod
    def action() -> PacketAction:
        """
        Returns the packet action associated with this packet.

        Returns:
            PacketAction: The packet action associated with this packet.
        """
        return PacketAction.Request

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        NpcRangeRequestClientPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "NpcRangeRequestClientPacket") -> None:
        """
        Serializes an instance of `NpcRangeRequestClientPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (NpcRangeRequestClientPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._npc_indexes_length is None:
                raise SerializationError("npc_indexes_length must be provided.")
            writer.add_char(data._npc_indexes_length)
            writer.add_byte(255)
            if data._npc_indexes is None:
                raise SerializationError("npc_indexes must be provided.")
            if len(data._npc_indexes) > 252:
                raise SerializationError(f"Expected length of npc_indexes to be 252 or less, got {len(data._npc_indexes)}.")
            for i in range(data._npc_indexes_length):
                writer.add_char(data._npc_indexes[i])
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "NpcRangeRequestClientPacket":
        """
        Deserializes an instance of `NpcRangeRequestClientPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            NpcRangeRequestClientPacket: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            npc_indexes_length = reader.get_char()
            reader.get_byte()
            npc_indexes = []
            for i in range(npc_indexes_length):
                npc_indexes.append(reader.get_char())
            result = NpcRangeRequestClientPacket(npc_indexes=npc_indexes)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"NpcRangeRequestClientPacket(byte_size={repr(self._byte_size)}, npc_indexes={repr(self._npc_indexes)})"
