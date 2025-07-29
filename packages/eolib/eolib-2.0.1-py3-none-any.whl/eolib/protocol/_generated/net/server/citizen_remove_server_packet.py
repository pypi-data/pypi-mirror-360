# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from .inn_unsubscribe_reply import InnUnsubscribeReply
from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class CitizenRemoveServerPacket(Packet):
    """
    Response to giving up citizenship of a town
    """
    _byte_size: int = 0
    _reply_code: InnUnsubscribeReply

    def __init__(self, *, reply_code: InnUnsubscribeReply):
        """
        Create a new instance of CitizenRemoveServerPacket.

        Args:
            reply_code (InnUnsubscribeReply): 
        """
        self._reply_code = reply_code

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def reply_code(self) -> InnUnsubscribeReply:
        return self._reply_code

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
        return PacketAction.Remove

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        CitizenRemoveServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "CitizenRemoveServerPacket") -> None:
        """
        Serializes an instance of `CitizenRemoveServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (CitizenRemoveServerPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._reply_code is None:
                raise SerializationError("reply_code must be provided.")
            writer.add_char(int(data._reply_code))
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "CitizenRemoveServerPacket":
        """
        Deserializes an instance of `CitizenRemoveServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            CitizenRemoveServerPacket: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            reply_code = InnUnsubscribeReply(reader.get_char())
            result = CitizenRemoveServerPacket(reply_code=reply_code)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"CitizenRemoveServerPacket(byte_size={repr(self._byte_size)}, reply_code={repr(self._reply_code)})"
