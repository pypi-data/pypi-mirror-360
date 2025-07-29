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

class MessageAcceptServerPacket(Packet):
    """
    Large message box
    """
    _byte_size: int = 0
    _messages: tuple[str, ...]

    def __init__(self, *, messages: Iterable[str]):
        """
        Create a new instance of MessageAcceptServerPacket.

        Args:
            messages (Iterable[str]): (Length must be `4`.)
        """
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
    def messages(self) -> tuple[str, ...]:
        return self._messages

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.Message

    @staticmethod
    def action() -> PacketAction:
        """
        Returns the packet action associated with this packet.

        Returns:
            PacketAction: The packet action associated with this packet.
        """
        return PacketAction.Accept

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        MessageAcceptServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "MessageAcceptServerPacket") -> None:
        """
        Serializes an instance of `MessageAcceptServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (MessageAcceptServerPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            writer.string_sanitization_mode = True
            if data._messages is None:
                raise SerializationError("messages must be provided.")
            if len(data._messages) != 4:
                raise SerializationError(f"Expected length of messages to be exactly 4, got {len(data._messages)}.")
            for i in range(4):
                writer.add_string(data._messages[i])
                writer.add_byte(0xFF)
            writer.string_sanitization_mode = False
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "MessageAcceptServerPacket":
        """
        Deserializes an instance of `MessageAcceptServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            MessageAcceptServerPacket: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            reader.chunked_reading_mode = True
            messages = []
            for i in range(4):
                messages.append(reader.get_string())
                reader.next_chunk()
            reader.chunked_reading_mode = False
            result = MessageAcceptServerPacket(messages=messages)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"MessageAcceptServerPacket(byte_size={repr(self._byte_size)}, messages={repr(self._messages)})"
