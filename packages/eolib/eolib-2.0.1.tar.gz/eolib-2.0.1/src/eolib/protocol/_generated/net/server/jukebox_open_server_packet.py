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

class JukeboxOpenServerPacket(Packet):
    """
    Reply to opening the jukebox listing
    """
    _byte_size: int = 0
    _map_id: int
    _jukebox_player: str

    def __init__(self, *, map_id: int, jukebox_player: str):
        """
        Create a new instance of JukeboxOpenServerPacket.

        Args:
            map_id (int): (Value range is 0-64008.)
            jukebox_player (str): 
        """
        self._map_id = map_id
        self._jukebox_player = jukebox_player

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def map_id(self) -> int:
        return self._map_id

    @property
    def jukebox_player(self) -> str:
        return self._jukebox_player

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
        return PacketAction.Open

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        JukeboxOpenServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "JukeboxOpenServerPacket") -> None:
        """
        Serializes an instance of `JukeboxOpenServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (JukeboxOpenServerPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._map_id is None:
                raise SerializationError("map_id must be provided.")
            writer.add_short(data._map_id)
            if data._jukebox_player is None:
                raise SerializationError("jukebox_player must be provided.")
            writer.add_string(data._jukebox_player)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "JukeboxOpenServerPacket":
        """
        Deserializes an instance of `JukeboxOpenServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            JukeboxOpenServerPacket: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            map_id = reader.get_short()
            jukebox_player = reader.get_string()
            result = JukeboxOpenServerPacket(map_id=map_id, jukebox_player=jukebox_player)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"JukeboxOpenServerPacket(byte_size={repr(self._byte_size)}, map_id={repr(self._map_id)}, jukebox_player={repr(self._jukebox_player)})"
