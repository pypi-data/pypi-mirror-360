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

class PlayersAcceptClientPacket(Packet):
    """
    #find command request
    """
    _byte_size: int = 0
    _name: str

    def __init__(self, *, name: str):
        """
        Create a new instance of PlayersAcceptClientPacket.

        Args:
            name (str): 
        """
        self._name = name

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def name(self) -> str:
        return self._name

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.Players

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
        PlayersAcceptClientPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "PlayersAcceptClientPacket") -> None:
        """
        Serializes an instance of `PlayersAcceptClientPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (PlayersAcceptClientPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._name is None:
                raise SerializationError("name must be provided.")
            writer.add_string(data._name)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "PlayersAcceptClientPacket":
        """
        Deserializes an instance of `PlayersAcceptClientPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            PlayersAcceptClientPacket: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            name = reader.get_string()
            result = PlayersAcceptClientPacket(name=name)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"PlayersAcceptClientPacket(byte_size={repr(self._byte_size)}, name={repr(self._name)})"
