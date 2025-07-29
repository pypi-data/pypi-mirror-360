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

class GuildRequestServerPacket(Packet):
    """
    Guild create request
    """
    _byte_size: int = 0
    _player_id: int
    _guild_identity: str

    def __init__(self, *, player_id: int, guild_identity: str):
        """
        Create a new instance of GuildRequestServerPacket.

        Args:
            player_id (int): (Value range is 0-64008.)
            guild_identity (str): 
        """
        self._player_id = player_id
        self._guild_identity = guild_identity

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def player_id(self) -> int:
        return self._player_id

    @property
    def guild_identity(self) -> str:
        return self._guild_identity

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
        return PacketAction.Request

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        GuildRequestServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "GuildRequestServerPacket") -> None:
        """
        Serializes an instance of `GuildRequestServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (GuildRequestServerPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._player_id is None:
                raise SerializationError("player_id must be provided.")
            writer.add_short(data._player_id)
            if data._guild_identity is None:
                raise SerializationError("guild_identity must be provided.")
            writer.add_string(data._guild_identity)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "GuildRequestServerPacket":
        """
        Deserializes an instance of `GuildRequestServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            GuildRequestServerPacket: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            player_id = reader.get_short()
            guild_identity = reader.get_string()
            result = GuildRequestServerPacket(player_id=player_id, guild_identity=guild_identity)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"GuildRequestServerPacket(byte_size={repr(self._byte_size)}, player_id={repr(self._player_id)}, guild_identity={repr(self._guild_identity)})"
