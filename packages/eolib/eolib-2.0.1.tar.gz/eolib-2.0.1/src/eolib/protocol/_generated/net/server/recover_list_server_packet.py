# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from .character_stats_update import CharacterStatsUpdate
from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class RecoverListServerPacket(Packet):
    """
    Stats update
    """
    _byte_size: int = 0
    _class_id: int
    _stats: CharacterStatsUpdate

    def __init__(self, *, class_id: int, stats: CharacterStatsUpdate):
        """
        Create a new instance of RecoverListServerPacket.

        Args:
            class_id (int): (Value range is 0-64008.)
            stats (CharacterStatsUpdate): 
        """
        self._class_id = class_id
        self._stats = stats

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def class_id(self) -> int:
        return self._class_id

    @property
    def stats(self) -> CharacterStatsUpdate:
        return self._stats

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.Recover

    @staticmethod
    def action() -> PacketAction:
        """
        Returns the packet action associated with this packet.

        Returns:
            PacketAction: The packet action associated with this packet.
        """
        return PacketAction.List

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        RecoverListServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "RecoverListServerPacket") -> None:
        """
        Serializes an instance of `RecoverListServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (RecoverListServerPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._class_id is None:
                raise SerializationError("class_id must be provided.")
            writer.add_short(data._class_id)
            if data._stats is None:
                raise SerializationError("stats must be provided.")
            CharacterStatsUpdate.serialize(writer, data._stats)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "RecoverListServerPacket":
        """
        Deserializes an instance of `RecoverListServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            RecoverListServerPacket: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            class_id = reader.get_short()
            stats = CharacterStatsUpdate.deserialize(reader)
            result = RecoverListServerPacket(class_id=class_id, stats=stats)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"RecoverListServerPacket(byte_size={repr(self._byte_size)}, class_id={repr(self._class_id)}, stats={repr(self._stats)})"
