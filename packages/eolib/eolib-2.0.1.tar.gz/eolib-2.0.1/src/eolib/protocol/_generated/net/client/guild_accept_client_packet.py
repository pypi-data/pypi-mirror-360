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

class GuildAcceptClientPacket(Packet):
    """
    Accept pending guild creation invite
    """
    _byte_size: int = 0
    _inviter_player_id: int

    def __init__(self, *, inviter_player_id: int):
        """
        Create a new instance of GuildAcceptClientPacket.

        Args:
            inviter_player_id (int): (Value range is 0-64008.)
        """
        self._inviter_player_id = inviter_player_id

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def inviter_player_id(self) -> int:
        return self._inviter_player_id

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.Guild

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
        GuildAcceptClientPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "GuildAcceptClientPacket") -> None:
        """
        Serializes an instance of `GuildAcceptClientPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (GuildAcceptClientPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            writer.add_int(20202)
            if data._inviter_player_id is None:
                raise SerializationError("inviter_player_id must be provided.")
            writer.add_short(data._inviter_player_id)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "GuildAcceptClientPacket":
        """
        Deserializes an instance of `GuildAcceptClientPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            GuildAcceptClientPacket: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            reader.get_int()
            inviter_player_id = reader.get_short()
            result = GuildAcceptClientPacket(inviter_player_id=inviter_player_id)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"GuildAcceptClientPacket(byte_size={repr(self._byte_size)}, inviter_player_id={repr(self._inviter_player_id)})"
