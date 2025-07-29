# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from __future__ import annotations
from collections.abc import Iterable
from .npc_map_info import NpcMapInfo
from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class NpcAgreeServerPacket(Packet):
    """
    Reply to request for information about nearby NPCs
    """
    _byte_size: int = 0
    _npcs_count: int
    _npcs: tuple[NpcMapInfo, ...]

    def __init__(self, *, npcs: Iterable[NpcMapInfo]):
        """
        Create a new instance of NpcAgreeServerPacket.

        Args:
            npcs (Iterable[NpcMapInfo]): (Length must be 252 or less.)
        """
        self._npcs = tuple(npcs)
        self._npcs_count = len(self._npcs)

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def npcs(self) -> tuple[NpcMapInfo, ...]:
        return self._npcs

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.Npc

    @staticmethod
    def action() -> PacketAction:
        """
        Returns the packet action associated with this packet.

        Returns:
            PacketAction: The packet action associated with this packet.
        """
        return PacketAction.Agree

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        NpcAgreeServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "NpcAgreeServerPacket") -> None:
        """
        Serializes an instance of `NpcAgreeServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (NpcAgreeServerPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._npcs_count is None:
                raise SerializationError("npcs_count must be provided.")
            writer.add_char(data._npcs_count)
            if data._npcs is None:
                raise SerializationError("npcs must be provided.")
            if len(data._npcs) > 252:
                raise SerializationError(f"Expected length of npcs to be 252 or less, got {len(data._npcs)}.")
            for i in range(data._npcs_count):
                NpcMapInfo.serialize(writer, data._npcs[i])
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "NpcAgreeServerPacket":
        """
        Deserializes an instance of `NpcAgreeServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            NpcAgreeServerPacket: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            npcs_count = reader.get_char()
            npcs = []
            for i in range(npcs_count):
                npcs.append(NpcMapInfo.deserialize(reader))
            result = NpcAgreeServerPacket(npcs=npcs)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"NpcAgreeServerPacket(byte_size={repr(self._byte_size)}, npcs={repr(self._npcs)})"
