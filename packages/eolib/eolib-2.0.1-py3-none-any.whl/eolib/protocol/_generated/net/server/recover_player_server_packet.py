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

class RecoverPlayerServerPacket(Packet):
    """
    HP/TP update
    """
    _byte_size: int = 0
    _hp: int
    _tp: int

    def __init__(self, *, hp: int, tp: int):
        """
        Create a new instance of RecoverPlayerServerPacket.

        Args:
            hp (int): (Value range is 0-64008.)
            tp (int): (Value range is 0-64008.)
        """
        self._hp = hp
        self._tp = tp

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def hp(self) -> int:
        return self._hp

    @property
    def tp(self) -> int:
        return self._tp

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
        return PacketAction.Player

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        RecoverPlayerServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "RecoverPlayerServerPacket") -> None:
        """
        Serializes an instance of `RecoverPlayerServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (RecoverPlayerServerPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._hp is None:
                raise SerializationError("hp must be provided.")
            writer.add_short(data._hp)
            if data._tp is None:
                raise SerializationError("tp must be provided.")
            writer.add_short(data._tp)
            writer.add_short(0)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "RecoverPlayerServerPacket":
        """
        Deserializes an instance of `RecoverPlayerServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            RecoverPlayerServerPacket: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            hp = reader.get_short()
            tp = reader.get_short()
            reader.get_short()
            result = RecoverPlayerServerPacket(hp=hp, tp=tp)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"RecoverPlayerServerPacket(byte_size={repr(self._byte_size)}, hp={repr(self._hp)}, tp={repr(self._tp)})"
