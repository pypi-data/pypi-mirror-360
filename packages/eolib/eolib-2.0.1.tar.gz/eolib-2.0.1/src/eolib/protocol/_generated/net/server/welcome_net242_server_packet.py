# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from .pub_file import PubFile
from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class WelcomeNet242ServerPacket(Packet):
    """
    Equivalent to INIT_INIT with InitReply.FileEnf
    """
    _byte_size: int = 0
    _pub_file: PubFile

    def __init__(self, *, pub_file: PubFile):
        """
        Create a new instance of WelcomeNet242ServerPacket.

        Args:
            pub_file (PubFile): 
        """
        self._pub_file = pub_file

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def pub_file(self) -> PubFile:
        return self._pub_file

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.Welcome

    @staticmethod
    def action() -> PacketAction:
        """
        Returns the packet action associated with this packet.

        Returns:
            PacketAction: The packet action associated with this packet.
        """
        return PacketAction.Net242

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        WelcomeNet242ServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "WelcomeNet242ServerPacket") -> None:
        """
        Serializes an instance of `WelcomeNet242ServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (WelcomeNet242ServerPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._pub_file is None:
                raise SerializationError("pub_file must be provided.")
            PubFile.serialize(writer, data._pub_file)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "WelcomeNet242ServerPacket":
        """
        Deserializes an instance of `WelcomeNet242ServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            WelcomeNet242ServerPacket: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            pub_file = PubFile.deserialize(reader)
            result = WelcomeNet242ServerPacket(pub_file=pub_file)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"WelcomeNet242ServerPacket(byte_size={repr(self._byte_size)}, pub_file={repr(self._pub_file)})"
