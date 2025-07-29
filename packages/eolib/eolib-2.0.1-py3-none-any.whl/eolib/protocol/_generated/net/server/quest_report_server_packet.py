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

class QuestReportServerPacket(Packet):
    """
    NPC chat messages
    """
    _byte_size: int = 0
    _npc_index: int
    _messages: tuple[str, ...]

    def __init__(self, *, npc_index: int, messages: Iterable[str]):
        """
        Create a new instance of QuestReportServerPacket.

        Args:
            npc_index (int): (Value range is 0-64008.)
            messages (Iterable[str]): 
        """
        self._npc_index = npc_index
        self._messages = tuple(messages)

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def npc_index(self) -> int:
        return self._npc_index

    @property
    def messages(self) -> tuple[str, ...]:
        return self._messages

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.Quest

    @staticmethod
    def action() -> PacketAction:
        """
        Returns the packet action associated with this packet.

        Returns:
            PacketAction: The packet action associated with this packet.
        """
        return PacketAction.Report

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        QuestReportServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "QuestReportServerPacket") -> None:
        """
        Serializes an instance of `QuestReportServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (QuestReportServerPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            writer.string_sanitization_mode = True
            if data._npc_index is None:
                raise SerializationError("npc_index must be provided.")
            writer.add_short(data._npc_index)
            writer.add_byte(0xFF)
            if data._messages is None:
                raise SerializationError("messages must be provided.")
            for i in range(len(data._messages)):
                writer.add_string(data._messages[i])
                writer.add_byte(0xFF)
            writer.string_sanitization_mode = False
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "QuestReportServerPacket":
        """
        Deserializes an instance of `QuestReportServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            QuestReportServerPacket: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            reader.chunked_reading_mode = True
            npc_index = reader.get_short()
            reader.next_chunk()
            messages = []
            while reader.remaining > 0:
                messages.append(reader.get_string())
                reader.next_chunk()
            reader.chunked_reading_mode = False
            result = QuestReportServerPacket(npc_index=npc_index, messages=messages)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"QuestReportServerPacket(byte_size={repr(self._byte_size)}, npc_index={repr(self._npc_index)}, messages={repr(self._messages)})"
