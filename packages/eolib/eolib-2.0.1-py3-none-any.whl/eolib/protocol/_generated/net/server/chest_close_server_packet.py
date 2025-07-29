# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from typing import cast
from typing import Optional
from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class ChestCloseServerPacket(Packet):
    """
    Reply to trying to interact with a locked or "broken" chest.
    The official client assumes a broken chest if the packet is under 2 bytes in length.
    """
    _byte_size: int = 0
    _key: Optional[int]

    def __init__(self, *, key: Optional[int] = None):
        """
        Create a new instance of ChestCloseServerPacket.

        Args:
            key (Optional[int]): Sent if the player is trying to interact with a locked chest (Value range is 0-64008.)
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
    def key(self) -> Optional[int]:
        """
        Sent if the player is trying to interact with a locked chest
        """
        return self._key

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.Chest

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
        ChestCloseServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "ChestCloseServerPacket") -> None:
        """
        Serializes an instance of `ChestCloseServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (ChestCloseServerPacket): The data to serialize.
        """
        old_writer_length: int = len(writer)
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            reached_missing_optional = data._key is None
            if not reached_missing_optional:
                writer.add_short(cast(int, data._key))
            if len(writer) == old_writer_length:
                writer.add_string("N")
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "ChestCloseServerPacket":
        """
        Deserializes an instance of `ChestCloseServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            ChestCloseServerPacket: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            key: Optional[int] = None
            if reader.remaining > 0:
                key = reader.get_short()
            if reader.position == reader_start_position:
                reader.get_string()
            result = ChestCloseServerPacket(key=key)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"ChestCloseServerPacket(byte_size={repr(self._byte_size)}, key={repr(self._key)})"
