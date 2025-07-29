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

class CitizenReplyServerPacket(Packet):
    """
    Response to subscribing to a town
    """
    _byte_size: int = 0
    _questions_wrong: int

    def __init__(self, *, questions_wrong: int):
        """
        Create a new instance of CitizenReplyServerPacket.

        Args:
            questions_wrong (int): (Value range is 0-252.)
        """
        self._questions_wrong = questions_wrong

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def questions_wrong(self) -> int:
        return self._questions_wrong

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.Citizen

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
        CitizenReplyServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "CitizenReplyServerPacket") -> None:
        """
        Serializes an instance of `CitizenReplyServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (CitizenReplyServerPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._questions_wrong is None:
                raise SerializationError("questions_wrong must be provided.")
            writer.add_char(data._questions_wrong)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "CitizenReplyServerPacket":
        """
        Deserializes an instance of `CitizenReplyServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            CitizenReplyServerPacket: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            questions_wrong = reader.get_char()
            result = CitizenReplyServerPacket(questions_wrong=questions_wrong)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"CitizenReplyServerPacket(byte_size={repr(self._byte_size)}, questions_wrong={repr(self._questions_wrong)})"
