# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ...direction import Direction
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class SpellTargetSelfClientPacket(Packet):
    """
    Self-targeted spell cast
    """
    _byte_size: int = 0
    _direction: Direction
    _spell_id: int
    _timestamp: int

    def __init__(self, *, direction: Direction, spell_id: int, timestamp: int):
        """
        Create a new instance of SpellTargetSelfClientPacket.

        Args:
            direction (Direction): 
            spell_id (int): (Value range is 0-64008.)
            timestamp (int): (Value range is 0-16194276.)
        """
        self._direction = direction
        self._spell_id = spell_id
        self._timestamp = timestamp

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def direction(self) -> Direction:
        return self._direction

    @property
    def spell_id(self) -> int:
        return self._spell_id

    @property
    def timestamp(self) -> int:
        return self._timestamp

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.Spell

    @staticmethod
    def action() -> PacketAction:
        """
        Returns the packet action associated with this packet.

        Returns:
            PacketAction: The packet action associated with this packet.
        """
        return PacketAction.TargetSelf

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        SpellTargetSelfClientPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "SpellTargetSelfClientPacket") -> None:
        """
        Serializes an instance of `SpellTargetSelfClientPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (SpellTargetSelfClientPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._direction is None:
                raise SerializationError("direction must be provided.")
            writer.add_char(int(data._direction))
            if data._spell_id is None:
                raise SerializationError("spell_id must be provided.")
            writer.add_short(data._spell_id)
            if data._timestamp is None:
                raise SerializationError("timestamp must be provided.")
            writer.add_three(data._timestamp)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "SpellTargetSelfClientPacket":
        """
        Deserializes an instance of `SpellTargetSelfClientPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            SpellTargetSelfClientPacket: The data to serialize.
        """
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            direction = Direction(reader.get_char())
            spell_id = reader.get_short()
            timestamp = reader.get_three()
            result = SpellTargetSelfClientPacket(direction=direction, spell_id=spell_id, timestamp=timestamp)
            result._byte_size = reader.position - reader_start_position
            return result
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"SpellTargetSelfClientPacket(byte_size={repr(self._byte_size)}, direction={repr(self._direction)}, spell_id={repr(self._spell_id)}, timestamp={repr(self._timestamp)})"
