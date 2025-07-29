# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from .map_file import MapFile
from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class WarpCreateServerPacket(Packet):
    """
    Equivalent to INIT_INIT with InitReply.MapMutation
    """
    _byte_size: int = 0
    _map_file: MapFile

    def __init__(self, *, map_file: MapFile):
        """
        Create a new instance of WarpCreateServerPacket.

        Args:
            map_file (MapFile): 
        """
        self._map_file = map_file

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def map_file(self) -> MapFile:
        return self._map_file

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.Warp

    @staticmethod
    def action() -> PacketAction:
        """
        Returns the packet action associated with this packet.

        Returns:
            PacketAction: The packet action associated with this packet.
        """
        return PacketAction.Create

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        WarpCreateServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "WarpCreateServerPacket") -> None:
        """
        Serializes an instance of `WarpCreateServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (WarpCreateServerPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._map_file is None:
                raise SerializationError("map_file must be provided.")
            MapFile.serialize(writer, data._map_file)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "WarpCreateServerPacket":
        """
        Deserializes an instance of `WarpCreateServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            WarpCreateServerPacket: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            map_file = MapFile.deserialize(reader)
            result = WarpCreateServerPacket(map_file=map_file)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"WarpCreateServerPacket(byte_size={repr(self._byte_size)}, map_file={repr(self._map_file)})"
