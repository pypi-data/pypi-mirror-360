# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ...coords import Coords
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class SitRemoveServerPacket(Packet):
    """
    Nearby player standing up
    """
    _byte_size: int = 0
    _player_id: int
    _coords: Coords

    def __init__(self, *, player_id: int, coords: Coords):
        """
        Create a new instance of SitRemoveServerPacket.

        Args:
            player_id (int): (Value range is 0-64008.)
            coords (Coords): 
        """
        self._player_id = player_id
        self._coords = coords

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
    def coords(self) -> Coords:
        return self._coords

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.Sit

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
        SitRemoveServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "SitRemoveServerPacket") -> None:
        """
        Serializes an instance of `SitRemoveServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (SitRemoveServerPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._player_id is None:
                raise SerializationError("player_id must be provided.")
            writer.add_short(data._player_id)
            if data._coords is None:
                raise SerializationError("coords must be provided.")
            Coords.serialize(writer, data._coords)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "SitRemoveServerPacket":
        """
        Deserializes an instance of `SitRemoveServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            SitRemoveServerPacket: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            player_id = reader.get_short()
            coords = Coords.deserialize(reader)
            result = SitRemoveServerPacket(player_id=player_id, coords=coords)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"SitRemoveServerPacket(byte_size={repr(self._byte_size)}, player_id={repr(self._player_id)}, coords={repr(self._coords)})"
