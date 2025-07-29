# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from .guild_info_type import GuildInfoType
from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class GuildTakeClientPacket(Packet):
    """
    Request guild description, rank list, or bank balance
    """
    _byte_size: int = 0
    _session_id: int
    _info_type: GuildInfoType
    _guild_tag: str

    def __init__(self, *, session_id: int, info_type: GuildInfoType, guild_tag: str):
        """
        Create a new instance of GuildTakeClientPacket.

        Args:
            session_id (int): (Value range is 0-4097152080.)
            info_type (GuildInfoType): 
            guild_tag (str): (Length must be `3`.)
        """
        self._session_id = session_id
        self._info_type = info_type
        self._guild_tag = guild_tag

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def session_id(self) -> int:
        return self._session_id

    @property
    def info_type(self) -> GuildInfoType:
        return self._info_type

    @property
    def guild_tag(self) -> str:
        return self._guild_tag

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
        return PacketAction.Take

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        GuildTakeClientPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "GuildTakeClientPacket") -> None:
        """
        Serializes an instance of `GuildTakeClientPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (GuildTakeClientPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._session_id is None:
                raise SerializationError("session_id must be provided.")
            writer.add_int(data._session_id)
            if data._info_type is None:
                raise SerializationError("info_type must be provided.")
            writer.add_short(int(data._info_type))
            if data._guild_tag is None:
                raise SerializationError("guild_tag must be provided.")
            if len(data._guild_tag) != 3:
                raise SerializationError(f"Expected length of guild_tag to be exactly 3, got {len(data._guild_tag)}.")
            writer.add_fixed_string(data._guild_tag, 3, False)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "GuildTakeClientPacket":
        """
        Deserializes an instance of `GuildTakeClientPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            GuildTakeClientPacket: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            session_id = reader.get_int()
            info_type = GuildInfoType(reader.get_short())
            guild_tag = reader.get_fixed_string(3, False)
            result = GuildTakeClientPacket(session_id=session_id, info_type=info_type, guild_tag=guild_tag)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"GuildTakeClientPacket(byte_size={repr(self._byte_size)}, session_id={repr(self._session_id)}, info_type={repr(self._info_type)}, guild_tag={repr(self._guild_tag)})"
