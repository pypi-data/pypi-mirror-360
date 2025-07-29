# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ...emote import Emote
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class EmoteReportClientPacket(Packet):
    """
    Doing an emote
    """
    _byte_size: int = 0
    _emote: Emote

    def __init__(self, *, emote: Emote):
        """
        Create a new instance of EmoteReportClientPacket.

        Args:
            emote (Emote): 
        """
        self._emote = emote

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def emote(self) -> Emote:
        return self._emote

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.Emote

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
        EmoteReportClientPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "EmoteReportClientPacket") -> None:
        """
        Serializes an instance of `EmoteReportClientPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (EmoteReportClientPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._emote is None:
                raise SerializationError("emote must be provided.")
            writer.add_char(int(data._emote))
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "EmoteReportClientPacket":
        """
        Deserializes an instance of `EmoteReportClientPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            EmoteReportClientPacket: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            emote = Emote(reader.get_char())
            result = EmoteReportClientPacket(emote=emote)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"EmoteReportClientPacket(byte_size={repr(self._byte_size)}, emote={repr(self._emote)})"
