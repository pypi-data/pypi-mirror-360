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

class JukeboxMsgClientPacket(Packet):
    """
    Requesting a song on a jukebox
    """
    _byte_size: int = 0
    _track_id: int

    def __init__(self, *, track_id: int):
        """
        Create a new instance of JukeboxMsgClientPacket.

        Args:
            track_id (int): This value is 0-indexed (Value range is 0-64008.)
        """
        self._track_id = track_id

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def track_id(self) -> int:
        """
        This value is 0-indexed
        """
        return self._track_id

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.Jukebox

    @staticmethod
    def action() -> PacketAction:
        """
        Returns the packet action associated with this packet.

        Returns:
            PacketAction: The packet action associated with this packet.
        """
        return PacketAction.Msg

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        JukeboxMsgClientPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "JukeboxMsgClientPacket") -> None:
        """
        Serializes an instance of `JukeboxMsgClientPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (JukeboxMsgClientPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            writer.add_char(0)
            writer.add_char(0)
            if data._track_id is None:
                raise SerializationError("track_id must be provided.")
            writer.add_short(data._track_id)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "JukeboxMsgClientPacket":
        """
        Deserializes an instance of `JukeboxMsgClientPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            JukeboxMsgClientPacket: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            reader.get_char()
            reader.get_char()
            track_id = reader.get_short()
            result = JukeboxMsgClientPacket(track_id=track_id)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"JukeboxMsgClientPacket(byte_size={repr(self._byte_size)}, track_id={repr(self._track_id)})"
