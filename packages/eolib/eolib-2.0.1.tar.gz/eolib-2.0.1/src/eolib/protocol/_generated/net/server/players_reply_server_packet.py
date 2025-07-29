# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from .players_list_friends import PlayersListFriends
from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class PlayersReplyServerPacket(Packet):
    """
    Equivalent to INIT_INIT with InitReply.PlayersListFriends
    """
    _byte_size: int = 0
    _players_list: PlayersListFriends

    def __init__(self, *, players_list: PlayersListFriends):
        """
        Create a new instance of PlayersReplyServerPacket.

        Args:
            players_list (PlayersListFriends): 
        """
        self._players_list = players_list

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def players_list(self) -> PlayersListFriends:
        return self._players_list

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
        return PacketAction.Reply

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        PlayersReplyServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "PlayersReplyServerPacket") -> None:
        """
        Serializes an instance of `PlayersReplyServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (PlayersReplyServerPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            writer.string_sanitization_mode = True
            if data._players_list is None:
                raise SerializationError("players_list must be provided.")
            PlayersListFriends.serialize(writer, data._players_list)
            writer.string_sanitization_mode = False
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "PlayersReplyServerPacket":
        """
        Deserializes an instance of `PlayersReplyServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            PlayersReplyServerPacket: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            reader.chunked_reading_mode = True
            players_list = PlayersListFriends.deserialize(reader)
            reader.chunked_reading_mode = False
            result = PlayersReplyServerPacket(players_list=players_list)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"PlayersReplyServerPacket(byte_size={repr(self._byte_size)}, players_list={repr(self._players_list)})"
