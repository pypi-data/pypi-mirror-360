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

class GuildKickClientPacket(Packet):
    """
    Kick member from guild
    """
    _byte_size: int = 0
    _session_id: int
    _member_name: str

    def __init__(self, *, session_id: int, member_name: str):
        """
        Create a new instance of GuildKickClientPacket.

        Args:
            session_id (int): (Value range is 0-4097152080.)
            member_name (str): 
        """
        self._session_id = session_id
        self._member_name = member_name

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
    def member_name(self) -> str:
        return self._member_name

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
        return PacketAction.Kick

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        GuildKickClientPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "GuildKickClientPacket") -> None:
        """
        Serializes an instance of `GuildKickClientPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (GuildKickClientPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._session_id is None:
                raise SerializationError("session_id must be provided.")
            writer.add_int(data._session_id)
            if data._member_name is None:
                raise SerializationError("member_name must be provided.")
            writer.add_string(data._member_name)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "GuildKickClientPacket":
        """
        Deserializes an instance of `GuildKickClientPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            GuildKickClientPacket: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            session_id = reader.get_int()
            member_name = reader.get_string()
            result = GuildKickClientPacket(session_id=session_id, member_name=member_name)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"GuildKickClientPacket(byte_size={repr(self._byte_size)}, session_id={repr(self._session_id)}, member_name={repr(self._member_name)})"
