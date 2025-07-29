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

class DoorCloseServerPacket(Packet):
    """
    Reply to trying to open a locked door
    """
    _byte_size: int = 0
    _key: int

    def __init__(self, *, key: int):
        """
        Create a new instance of DoorCloseServerPacket.

        Args:
            key (int): (Value range is 0-252.)
        """
        self._key = key

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def key(self) -> int:
        return self._key

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.Door

    @staticmethod
    def action() -> PacketAction:
        """
        Returns the packet action associated with this packet.

        Returns:
            PacketAction: The packet action associated with this packet.
        """
        return PacketAction.Close

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        DoorCloseServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "DoorCloseServerPacket") -> None:
        """
        Serializes an instance of `DoorCloseServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (DoorCloseServerPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._key is None:
                raise SerializationError("key must be provided.")
            writer.add_char(data._key)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "DoorCloseServerPacket":
        """
        Deserializes an instance of `DoorCloseServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            DoorCloseServerPacket: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            key = reader.get_char()
            result = DoorCloseServerPacket(key=key)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"DoorCloseServerPacket(byte_size={repr(self._byte_size)}, key={repr(self._key)})"
