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

class MessageOpenServerPacket(Packet):
    """
    Status bar message
    """
    _byte_size: int = 0
    _message: str

    def __init__(self, *, message: str):
        """
        Create a new instance of MessageOpenServerPacket.

        Args:
            message (str): 
        """
        self._message = message

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def message(self) -> str:
        return self._message

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
        return PacketAction.Open

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        MessageOpenServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "MessageOpenServerPacket") -> None:
        """
        Serializes an instance of `MessageOpenServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (MessageOpenServerPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._message is None:
                raise SerializationError("message must be provided.")
            writer.add_string(data._message)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "MessageOpenServerPacket":
        """
        Deserializes an instance of `MessageOpenServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            MessageOpenServerPacket: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            message = reader.get_string()
            result = MessageOpenServerPacket(message=message)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"MessageOpenServerPacket(byte_size={repr(self._byte_size)}, message={repr(self._message)})"
